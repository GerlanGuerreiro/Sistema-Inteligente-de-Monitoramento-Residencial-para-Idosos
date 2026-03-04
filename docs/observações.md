📘 Observação Acadêmica Importante

No TCC, explicaremos que:

O uso de .env garante segurança e boas práticas DevOps

A containerização garante isolamento e reprodutibilidade

O uso de variáveis em português melhora a legibilidade acadêmica

🚀 Recomendação para seu TCC

Para um projeto acadêmico bem estruturado:
| Arquivo              | Função                     |
| -------------------- | -------------------------- |
| README.md (raiz)     | Apresentação do projeto    |
| docs/TCC_COMPLETO.md | Estrutura formal acadêmica |
| docs/diagramas/      | Imagens UML                |
| docs/referencias.md  | Referências ABNT           |

📘 Justificativa Acadêmica (Para o TCC)

A utilização do protocolo MQTT foi escolhida por:

Baixo consumo de recursos

Comunicação assíncrona

Padrão amplamente utilizado em IoT

Ideal para arquiteturas desacopladas


🎓 O Que Você Pode Escrever no TCC

Esta etapa demonstra:

Arquitetura orientada a eventos

Uso de protocolo MQTT

Comunicação assíncrona

Desacoplamento entre NVR e backend

Base para sistema de regras inteligentes


Modelagem do Banco de Dados
🎯 Tabela: eventos_monitoramento
Estrutura
Campo	Tipo	Descrição
id	SERIAL	Identificador único
tipo_evento	VARCHAR	Tipo do evento (ex: deteccao_pessoa)
objeto_detectado	VARCHAR	Objeto identificado
horario_evento	TIMESTAMP	Horário do evento
camera	VARCHAR	Identificação da câmera
criado_em	TIMESTAMP	Data de registro no sistema
