"""Generación local con un modelo instruct y referencias al corpus."""
import re
from functools import lru_cache

SIN_EVIDENCIA = "Los apuntes disponibles no alcanzan para responder esa pregunta."


@lru_cache(maxsize=1)
def cargar_modelo():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    nombre = "Qwen/Qwen2.5-1.5B-Instruct"
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    tipo = torch.float16 if dispositivo == "cuda" else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(nombre)
    modelo = AutoModelForCausalLM.from_pretrained(nombre, torch_dtype=tipo)
    return tokenizer, modelo.to(dispositivo).eval()


def generar(pregunta, evidencia):
    if not evidencia:
        return SIN_EVIDENCIA

    import torch

    tokenizer, modelo = cargar_modelo()
    contexto = "\n".join(f'[{f["id"]}] {f["texto"]}' for f in evidencia)
    mensajes = [
        {"role": "system", "content":
         "Eres tutor de Python. Usa únicamente los apuntes como evidencia. "
         "Responde en español en una o dos frases y cita el número entre corchetes. "
         "Si falta información, responde exactamente: " + SIN_EVIDENCIA},
        {"role": "user", "content": f"Apuntes:\n{contexto}\n\nPregunta: {pregunta}"}
    ]
    prompt = tokenizer.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True)
    entrada = tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(modelo.device)
    with torch.inference_mode():
        salida = modelo.generate(**entrada, max_new_tokens=140, do_sample=False,
                                 pad_token_id=tokenizer.eos_token_id)
    # La salida también incluye la pregunta. Mostramos solo lo que escribió el modelo.
    nuevos = salida[0, entrada["input_ids"].shape[1]:]
    respuesta = tokenizer.decode(nuevos, skip_special_tokens=True).strip()
    if respuesta == SIN_EVIDENCIA:
        return respuesta
    citados = set(re.findall(r"\[(\d+)\]", respuesta))
    disponibles = {str(f["id"]) for f in evidencia}
    if not citados or not citados <= disponibles:
        return "El modelo no citó correctamente los apuntes. Revisa los fragmentos recuperados."
    return respuesta
