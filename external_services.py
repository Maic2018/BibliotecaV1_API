"""
Clientes para os serviços externos consumidos pela API da Biblioteca.

- OpenLibraryClient: busca metadados e capa de um livro pelo título,
  usando a API pública da Open Library (openlibrary.org). Não exige
  cadastro nem chave de API.
- ViaCepClient: busca o endereço de uma unidade da biblioteca a partir
  do CEP, usando a API pública ViaCEP (viacep.com.br). Não exige
  cadastro nem chave de API.

Os dados retornados por ambas as APIs são sempre tratados/normalizados
aqui antes de chegar às rotas: nenhuma chamada redireciona o usuário
para o site externo, apenas os dados (texto/URL de imagem) são
reaproveitados dentro da própria aplicação.
"""
import re
import requests

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPEN_LIBRARY_COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
VIA_CEP_URL = "https://viacep.com.br/ws/{cep}/json/"

REQUEST_TIMEOUT = 5  # segundos


class OpenLibraryClient:
    def search_book(self, title):
        """Consulta a Open Library pelo título e devolve um dicionário
        com autor, ano de publicação e URL da capa (quando disponíveis).
        Retorna None se nada for encontrado ou se o serviço externo falhar.
        """
        if not title:
            return None

        try:
            response = requests.get(
                OPEN_LIBRARY_SEARCH_URL,
                params={"q": title, "limit": 1},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException:
            return None

        data = response.json()
        docs = data.get("docs") or []
        if not docs:
            return None

        doc = docs[0]
        authors = doc.get("author_name") or []
        cover_id = doc.get("cover_i")

        return {
            "title": doc.get("title", title),
            "author": authors[0] if authors else None,
            "first_publish_year": doc.get("first_publish_year"),
            "image_url": OPEN_LIBRARY_COVER_URL.format(cover_id=cover_id) if cover_id else None,
        }


class ViaCepClient:
    def lookup(self, cep):
        """Consulta o ViaCEP pelo CEP informado e devolve um dicionário
        com logradouro, bairro, cidade e UF. Retorna None se o CEP for
        inválido, não existir ou o serviço externo falhar.
        """
        cleaned_cep = re.sub(r"\D", "", cep or "")
        if len(cleaned_cep) != 8:
            return None

        try:
            response = requests.get(
                VIA_CEP_URL.format(cep=cleaned_cep),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException:
            return None

        data = response.json()
        if data.get("erro"):
            return None

        return {
            "cep": data.get("cep", cleaned_cep),
            "logradouro": data.get("logradouro"),
            "bairro": data.get("bairro"),
            "cidade": data.get("localidade"),
            "uf": data.get("uf"),
        }
