import requests
import os
import json
import csv

from datetime import datetime
from dotenv import load_dotenv
from groq import Groq


# ==========================================
# CONFIGURACIÓN
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

API_URL = "http://127.0.0.1:8000"

LOG_FILE = "conversation_log.csv"


# ==========================================
# FUNCIONES / TOOLS
# ==========================================

def get_inventory():
    response = requests.get(f"{API_URL}/inventory")
    return response.json()


def create_product(product):
    response = requests.post(
        f"{API_URL}/inventory",
        json=product
    )
    return response.json()


def update_product(product_id, product):
    response = requests.patch(
        f"{API_URL}/inventory/{product_id}",
        json=product
    )
    return response.json()


def get_inventory_alerts():
    response = requests.get(f"{API_URL}/inventory/alerts")
    return response.json()


# ==========================================
# CATÁLOGO DE TOOLS
# ==========================================

tools = {
    "get_inventory": {
        "description": (
            "Obtiene todos los productos del inventario. "
            "No necesita argumentos."
        ),
        "function": get_inventory
    },

    "create_product": {
        "description": (
            "Crea un nuevo producto en el inventario. "
            "Recibe product, un diccionario con los datos del producto."
        ),
        "function": create_product
    },

    "update_product": {
        "description": (
            "Actualiza un producto existente. "
            "Recibe product_id y product, un diccionario con los campos a actualizar."
        ),
        "function": update_product
    },

    "get_inventory_alerts": {
        "description": (
            "Obtiene los productos que tienen un nivel de stock bajo. "
            "No necesita argumentos."
        ),
        "function": get_inventory_alerts
    }
}


# ==========================================
# SYSTEM PROMPT
# ==========================================

def build_system_prompt(tools):

    tools_description = ""

    for tool_name, tool_info in tools.items():
        tools_description += (
            f"- {tool_name}: {tool_info['description']}\n"
        )

    system_prompt = f"""
Eres un agente encargado de gestionar un inventario.

Tienes disponibles estas herramientas:

{tools_description}

Tu trabajo es decidir qué hacer para responder correctamente
a la petición del usuario.

No ejecutes herramientas directamente.
No inventes información sobre el inventario.

Si necesitas utilizar una herramienta, responde únicamente
con JSON usando este formato:

{{
    "action": "use_tool",
    "name": "nombre_de_la_herramienta",
    "arguments": {{}}
}}

Si ya tienes suficiente información para responder al usuario,
responde únicamente con JSON usando este formato:

{{
    "action": "final_answer",
    "answer": "respuesta para el usuario"
}}

No escribas ningún texto fuera del JSON.
"""

    return system_prompt


# ==========================================
# LOG
# ==========================================

def log_conversation(actor, message, tool_call=""):

    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "actor",
                "message",
                "tool_call",
                "timestamp"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "actor": actor,
            "message": message,
            "tool_call": tool_call,
            "timestamp": datetime.now().isoformat()
        })


# ==========================================
# AGENTE
# ==========================================

def run_agent(user_input, max_iterations=5):

    system_prompt = build_system_prompt(tools)

    memory = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    log_conversation(
        actor="user",
        message=user_input
    )

    for iteration in range(max_iterations):

        # ----------------------------------
        # 1. PREGUNTAMOS AL LLM
        # ----------------------------------

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=memory
        )

        response_text = completion.choices[0].message.content

        log_conversation(
            actor="assistant",
            message=response_text
        )

        # ----------------------------------
        # 2. INTERPRETAMOS SU DECISIÓN
        # ----------------------------------

        try:
            decision = json.loads(response_text)

        except json.JSONDecodeError:
            return "El LLM ha devuelto una respuesta que no es JSON válido."

        action = decision.get("action")

        # ----------------------------------
        # 3. RESPUESTA FINAL
        # ----------------------------------

        if action == "final_answer":

            answer = decision.get("answer", "")

            return answer

        # ----------------------------------
        # 4. USO DE UNA TOOL
        # ----------------------------------

        if action == "use_tool":

            tool_name = decision.get("name")
            arguments = decision.get("arguments", {})

            # Comprobamos que la herramienta existe
            if tool_name not in tools:
                return f"Herramienta desconocida: {tool_name}"

            tool_function = tools[tool_name]["function"]

            try:
                result = tool_function(**arguments)

            except Exception as error:
                result = {
                    "error": str(error)
                }

            log_conversation(
                actor="tool",
                message=json.dumps(
                    result,
                    ensure_ascii=False
                ),
                tool_call=tool_name
            )

            # ----------------------------------
            # 5. ACTUALIZAMOS LA MEMORIA
            # ----------------------------------

            memory.append({
                "role": "assistant",
                "content": response_text
            })

            memory.append({
                "role": "user",
                "content": (
                    f"Resultado de la herramienta "
                    f"{tool_name}:\n"
                    f"{json.dumps(result, ensure_ascii=False)}"
                )
            })

            # El for vuelve a empezar.
            # El LLM recibe ahora también el resultado
            # de la herramienta.

            continue

        return "El agente ha devuelto una acción desconocida."

    return "El agente alcanzó el límite máximo de iteraciones."


# ==========================================
# EJECUCIÓN DESDE TERMINAL
# ==========================================

if __name__ == "__main__":

    user_question = input(
        "¿Qué quieres preguntarle al agente? "
    )

    answer = run_agent(user_question)

    print("\nAgente:")
    print(answer)