
import bcrypt
from core.database import executar_consulta

def autenticar_usuario(usuario, senha):
    query = "SELECT * FROM usuarios WHERE usuario = %s"
    resultados = executar_consulta(query, (usuario,), fetch=True, dictionary=True)

    if resultados:
        resultado = resultados[0]
        senha_armazenada = resultado['senha']
        if bcrypt.checkpw(senha.encode(), senha_armazenada.encode()):
            return resultado
    return None
