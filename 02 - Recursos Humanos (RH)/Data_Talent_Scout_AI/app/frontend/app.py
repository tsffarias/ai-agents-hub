import streamlit as st
import requests
import time
import json
import re
from sendmail import send_email

def search_jobs(requirements):
    url = 'http://nginx/research_candidates'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = {'job_requirements': requirements}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Função para processar a Análise SWOT
def parse_swot(swot_data):
    """
    Retorna um dicionário com chaves Forças, Fraquezas, Oportunidades, Ameaças.
    Se swot_data for um dict, retorna tal dict.
    Se for string, aplica regex para extrair cada parte.
    Caso contrário, converte pra string e tenta extrair.
    """
    if isinstance(swot_data, dict):
        # Já é um dicionário. Simplesmente retorná-lo (ou adequar chaves, se necessário).
        return swot_data

    if not isinstance(swot_data, str):
        # Se não for string, converte
        swot_data = str(swot_data)

    pattern = r'(Forças|Fraquezas|Oportunidades|Ameaças):\s*(.*?)(?=$|Forças:|Fraquezas:|Oportunidades:|Ameaças:)'
    matches = re.findall(pattern, swot_data, flags=re.DOTALL)

    swot_dict = {}
    for key, value in matches:
        swot_dict[key] = value.strip()

    return swot_dict

def build_email_html(candidates, elapsed_time, token_usage=None):
    """
    Cria um HTML bem formatado com a lista de candidatos
    """
    html_start = f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body {{
            font-family: Arial, sans-serif;
            color: #333;
          }}
          .candidate {{
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 15px;
          }}
          .swot-title {{
            font-weight: bold;
            margin-top: 10px;
          }}
          .score {{
            font-weight: bold;
            color: #00539C;
          }}
          .metrics {{
            margin-top: 20px;
            font-style: italic;
            color: #666;
          }}
        </style>
      </head>
      <body>
        <h2>Resultados da Busca de Candidatos</h2>
        <p>Tempo de Execução: {elapsed_time:.2f} segundos</p>
    """

    # Se houver métricas de uso de tokens, exibir
    if token_usage:
        total_tokens = token_usage.get("total_tokens", "N/A")
        successful_requests = token_usage.get("successful_requests", "N/A")
        html_start += f"""
        <div class="metrics">
          <p>🔢 Tokens Usados: <strong>{total_tokens}</strong></p>
          <p>📈 Total de Requisições: <strong>{successful_requests}</strong></p>
        </div>
        """

    html_middle = ""
    for idx, c in enumerate(candidates, start=1):
        swot_parsed = parse_swot(c["Analise_SWOT"])
        html_middle += f"""
        <div class="candidate">
          <h3>👤 {c['Nome']}</h3>
          <p>📞 <strong>Contato:</strong> <a href="{c['Contato']}">{c['Contato']}</a></p>
          <p>📝 <strong>Descrição:</strong> {c['Descricao']}</p>
          <p class="score">📊 Score de Adequação: {c['Score_de_adequacao']}</p>

          <div class="swot-title">🔍 Análise SWOT</div>
          <ul>
            <li><strong>Forças:</strong> {swot_parsed.get('Forças', 'Não disponível')}</li>
            <li><strong>Fraquezas:</strong> {swot_parsed.get('Fraquezas', 'Não disponível')}</li>
            <li><strong>Oportunidades:</strong> {swot_parsed.get('Oportunidades', 'Não disponível')}</li>
            <li><strong>Ameaças:</strong> {swot_parsed.get('Ameaças', 'Não disponível')}</li>
          </ul>
        </div>
        """

    html_end = """
      </body>
    </html>
    """

    return html_start + html_middle + html_end

def main():
    st.title('🔍 Data Talent Scout AI')
    st.subheader("Insira os requisitos da vaga para encontrar os melhores perfis.")

    requirements = st.text_area(
        "✍️ Descreva os requisitos da vaga:", 
        height=150, 
        placeholder="Exemplo: Data Engineer, experiência com AWS e Python..."
    )

    if st.button('Buscar Candidatos'):
        st.session_state.button1_clicked = True

    if st.session_state.get("button1_clicked", False):
        start_time = time.time()
        with st.spinner('Buscando os melhores candidatos...'):
            results = search_jobs(requirements)
            end_time = time.time()
            elapsed_time = end_time - start_time

            if results and "result" in results:
                st.success("✅ Busca concluída!")
                st.markdown(f"**⏱ Tempo de execução: `{elapsed_time:.2f} segundos`**")

                # 🎯 Extrair candidatos do campo "raw" em results["result"]
                raw_candidates = results["result"].get("raw", None)
                token_usage = results["result"].get("token_usage", {})

                if raw_candidates:
                    try:
                        candidates = json.loads(raw_candidates)
                    except json.JSONDecodeError:
                        candidates = []

                    if candidates:
                        st.markdown("### 📌 **Top 5 Candidatos**")
                        for idx, candidate in enumerate(candidates):
                            with st.expander(f"👤 {candidate['Nome']}"):
                                st.markdown(f"📞 **Contato:** [{candidate['Contato']}]({candidate['Contato']})")
                                st.markdown(f"📝 **Descrição:** {candidate['Descricao']}")
                                
                                swot = parse_swot(candidate["Analise_SWOT"])
                                st.markdown("🔍 **Análise SWOT**")
                                st.markdown(f"- **Forças:** {swot.get('Forças', 'Não disponível')}")
                                st.markdown(f"- **Fraquezas:** {swot.get('Fraquezas', 'Não disponível')}")
                                st.markdown(f"- **Oportunidades:** {swot.get('Oportunidades', 'Não disponível')}")
                                st.markdown(f"- **Ameaças:** {swot.get('Ameaças', 'Não disponível')}")

                                st.metric("📊 Score de Adequação", candidate["Score_de_adequacao"])
                    
                        # ⚙️ Exibir métricas se existirem
                        if token_usage:
                            st.markdown("### ⚙️ **Métricas de Uso**")
                            st.metric("🔢 Tokens Usados", token_usage.get("total_tokens", "N/A"))
                            st.metric("📈 Total de Requisições", token_usage.get("successful_requests", "N/A"))

                        # Form para enviar email
                        st.markdown("### **Enviar Resultado por E-mail**")
                        with st.form("email_form"):
                            email_input = st.text_input("Digite o e-mail do destinatário:")
                            send_button = st.form_submit_button("Enviar E-mail")

                            if send_button:
                                if email_input.strip():
                                    # Monta o HTML do email
                                    html_content = build_email_html(candidates, elapsed_time, token_usage)
                                    # Envia o e-mail (ajuste a função conforme necessário)
                                    send_email(
                                        to_email=email_input.strip(),
                                        subject="Resultados Data Talent Scout AI",
                                        html_message=html_content
                                    )
                                    st.markdown("<h3 style='color:green;'>E-mail enviado com sucesso!</h3>", unsafe_allow_html=True)
                                else:
                                    st.error("Por favor, insira um endereço de e-mail válido.")
                        
                    else:
                        st.error("❌ Não há candidatos válidos no campo 'raw'.")
                else:
                    st.error("❌ Campo 'raw' não encontrado no response.")
            else:
                st.error("❌ Não foi possível encontrar candidatos para os requisitos informados.")

if __name__ == "__main__":
    main()
