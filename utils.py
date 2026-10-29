"""Funções de validação e tratamento de imagem (sem dependência de Flask)."""
import io
import re

from PIL import Image, ImageOps, UnidentifiedImageError

EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$"
)
CATEGORIAS = {"Aniversário", "Encontro", "Reunião", "Família", "Outro"}
FORMATOS = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp"}


def email_valido(email):
    return len(email) <= 150 and bool(EMAIL_RE.match(email))


def telefone_valido(digitos):
    """Aceita só dígitos: DDD (11-99) + 8 dígitos, ou + 9 dígitos começando em 9."""
    if len(digitos) not in (10, 11) or int(digitos[:2]) < 11:
        return False
    return len(digitos) == 10 or digitos[2] == "9"


def nome_valido(nome):
    return 2 <= len(nome) <= 150 and any(c.isalpha() for c in nome)


def processar_imagem(stream, max_lado=512):
    """Valida pelo conteúdo real, remove EXIF e reduz. Retorna (bytes, extensão)."""
    msg = "O arquivo não é uma imagem válida."
    try:
        with Image.open(stream) as img:
            if img.format not in FORMATOS:
                raise ValueError(msg)
            fmt = img.format
            img.load()
            img = ImageOps.exif_transpose(img)
            img.thumbnail((max_lado, max_lado))
            if fmt == "JPEG" and img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            saida = io.BytesIO()
            img.save(saida, format=fmt)  # sem exif= -> metadados descartados
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
        raise ValueError(msg)
    return saida.getvalue(), FORMATOS[fmt]
