# 🤖 RAG Generation - Sistema de Geração de Respostas

Este documento explica como o sistema RAG (Retrieval-Augmented Generation) gera respostas inteligentes baseadas nos documentos processados.

## 🧠 Arquitetura do Sistema RAG

```
Documentos PDF → Extração de Texto → Chunking → Embeddings → Busca Semântica → Geração de Resposta
```

## 📊 Fluxo de Geração de Respostas

### 1. **Processamento de Documentos**
```python
# Extração de texto dos PDFs
documents = processor.process_documents()

# Criação de chunks sobrepostos
chunks = processor.create_chunks(chunk_size=1000, overlap=200)
```

### 2. **Geração de Embeddings**
```python
# Cada chunk é convertido em vetor de embeddings
for chunk in chunks:
    embedding = client.embeddings.create(
        model="text-embedding-3-large",
        input=chunk['content']
    )
```

### 3. **Busca Semântica**
```python
# Pergunta do usuário é convertida em embedding
query_embedding = client.embeddings.create(
    model="text-embedding-3-small", 
    input=user_question
)

# Cálculo de similaridade com todos os chunks
similarities = cosine_similarity(query_embedding, chunk_embeddings)
```

### 4. **Geração de Resposta**
```python
# Contexto relevante é enviado para GPT-4.1
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": "Você é um especialista em soldagem..."},
        {"role": "user", "content": f"Pergunta: {question}\nContexto: {context}"}
    ]
)
```

## 🔍 Modelos de Embedding Utilizados

### **text-embedding-3-large** (Para Documentos)
- **Dimensões**: 3072
- **Uso**: Chunks dos documentos
- **Vantagem**: Maior precisão para conteúdo complexo

### **text-embedding-3-small** (Para Consultas)
- **Dimensões**: 1536  
- **Uso**: Perguntas dos usuários
- **Vantagem**: Maior velocidade e eficiência

## 📈 Algoritmo de Similaridade

```python
def find_relevant_chunks(query, top_k=5):
    # 1. Converter pergunta em embedding
    query_embedding = get_embedding(query)
    
    # 2. Calcular similaridade com todos os chunks
    similarities = []
    for chunk_data in chunk_embeddings:
        similarity = cosine_similarity([query_embedding], [chunk_data['embedding']])[0][0]
        similarities.append((similarity, chunk_data))
    
    # 3. Ordenar por relevância e retornar top_k
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [chunk_data for _, chunk_data in similarities[:top_k]]
```

## 🎯 Estratégias de Chunking

### **Chunking por Caracteres**
- **Tamanho**: 1000 caracteres
- **Sobreposição**: 200 caracteres
- **Filtro**: Chunks com menos de 100 caracteres são descartados

### **Benefícios da Sobreposição**
- ✅ Mantém contexto entre chunks
- ✅ Evita perda de informações nas bordas
- ✅ Melhora a recuperação de informações

## 💾 Sistema de Cache de Embeddings

### **Salvamento Automático**
```python
# Embeddings são salvos em:
embedding_folder/embeddings.pkl
```

### **Carregamento Inteligente**
```python
# Sistema verifica se embeddings existem
if embedding_file.exists():
    agent.load_embeddings()  # Carrega do cache
else:
    agent.process_and_embed_documents()  # Processa novos
```

### **Vantagens do Cache**
- ⚡ **Velocidade**: Evita reprocessamento
- 💰 **Economia**: Reduz custos de API
- 🔄 **Eficiência**: Atualizações incrementais

## 🧪 Processo de Geração Detalhado

### **Input**: Pergunta do Usuário
```
"Como funciona o processo de recebimento de notas fiscais?"
```

### **Step 1**: Embedding da Pergunta
```python
query_embedding = [0.1, -0.3, 0.8, ...]  # 1536 dimensões
```

### **Step 2**: Busca nos Chunks
```python
# Top 5 chunks mais relevantes:
chunks = [
    {"similarity": 0.89, "content": "Processo de recebimento...", "source": "documento1.pdf"},
    {"similarity": 0.85, "content": "Notas fiscais devem...", "source": "documento2.pdf"},
    # ... mais chunks
]
```

### **Step 3**: Construção do Contexto
```python
context = """
Document: documento1.pdf
Content: Processo de recebimento de notas fiscais...
---
Document: documento2.pdf  
Content: Notas fiscais devem ser...
"""
```

### **Step 4**: Prompt para GPT-4.1
```python
prompt = f"""
Baseado no contexto fornecido, responda a pergunta do usuário.
Se a informação não estiver disponível, declare isso claramente.

Pergunta: {question}
Contexto: {context}
"""
```

### **Output**: Resposta Gerada
```python
response = {
    'answer': 'O processo de recebimento de notas fiscais...',
    'sources': ['documento1.pdf', 'documento2.pdf'],
    'confidence': 0.85,
    'context_used': 'Processo de recebimento...'
}
```

## 🎛️ Parâmetros Configuráveis

### **Chunking**
```python
chunk_size = 1000      # Tamanho dos chunks
overlap = 200          # Sobreposição entre chunks
min_chunk_size = 100   # Tamanho mínimo válido
```

### **Busca**
```python
top_k = 5             # Número de chunks relevantes
similarity_threshold = 0.1  # Limiar de similaridade mínima
```

### **Geração**
```python
model = "gpt-4.1"     # Modelo de geração
temperature = 0.7      # Criatividade da resposta
max_tokens = 1000     # Limite de tokens na resposta
```

## 📊 Métricas de Qualidade

### **Similaridade de Embeddings**
- **Alta (>0.8)**: Informação muito relevante
- **Média (0.5-0.8)**: Informação moderadamente relevante  
- **Baixa (<0.5)**: Informação pouco relevante

### **Cobertura de Documentos**
- **Fonte única**: Resposta baseada em 1 documento
- **Múltiplas fontes**: Resposta baseada em vários documentos
- **Sem fonte**: Informação não encontrada nos documentos

## 🔧 Otimizações Implementadas

### **1. Embeddings Diferenciados**
- Documentos: `text-embedding-3-large` (maior precisão)
- Consultas: `text-embedding-3-small` (maior velocidade)

### **2. Cache Inteligente**
- Embeddings são salvos após primeira geração
- Carregamento automático em execuções subsequentes
- Atualização incremental quando documentos mudam

### **3. Chunking Otimizado**
- Sobreposição para manter contexto
- Filtro de chunks muito pequenos
- Preservação de estrutura do documento

### **4. Busca Eficiente**
- Cálculo de similaridade vetorizado
- Ordenação otimizada dos resultados
- Limitação do número de chunks processados

## 🚀 Performance e Escalabilidade

### **Benchmarks Típicos**
- **Processamento**: ~2-3 segundos por documento PDF
- **Embedding**: ~0.5 segundos por chunk
- **Busca**: ~0.1 segundos por consulta
- **Geração**: ~2-5 segundos por resposta

### **Limitações Atuais**
- **Tamanho máximo**: ~50 documentos por execução
- **Memória**: ~2GB para 1000 chunks
- **API Rate Limits**: 60 requests/minuto (OpenAI)

## 🔮 Melhorias Futuras

### **1. Embeddings Locais**
- Implementação de modelos de embedding locais
- Redução de dependência da API OpenAI
- Maior controle sobre os embeddings

### **2. Busca Híbrida**
- Combinação de busca semântica e textual
- Melhoria na precisão da recuperação
- Suporte a consultas mais complexas

### **3. Cache Distribuído**
- Sistema de cache compartilhado
- Otimização para múltiplos usuários
- Redução de reprocessamento

### **4. Fine-tuning**
- Treinamento específico para domínio
- Melhoria na qualidade das respostas
- Adaptação ao vocabulário técnico

---

**Sistema RAG desenvolvido para AtendentePRO** 🤖✨
