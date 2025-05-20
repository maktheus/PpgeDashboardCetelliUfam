# Análise de KPIs para Avaliação CAPES - Programa de Pós-Graduação em Engenharias IV

Este documento apresenta uma análise dos indicadores (KPIs) utilizados pela CAPES para avaliação de programas de pós-graduação em Engenharias IV, identificando quais podem ser implementados com os dados atuais disponíveis no sistema e quais necessitam de fontes adicionais de dados.

## KPIs Atualmente Implementados

O sistema atual já implementa os seguintes indicadores:

1. **Total de Alunos**: Contagem do número total de alunos no programa
2. **Total de Docentes**: Contagem do número total de docentes orientadores
3. **Tempo Médio até Defesa**: Tempo médio entre matrícula e defesa (em meses)
4. **Taxa de Sucesso na Defesa**: Percentual de defesas aprovadas
5. **Mediana do Tempo até Defesa**: Valor central do tempo até a defesa
6. **Tempo Médio por Programa**: Tempo médio para Mestrado e Doutorado separadamente
7. **Variação do Tempo (Desvio)**: Desvio padrão do tempo até a defesa
8. **Eficiência de Tempo**: Relação entre tempo esperado e tempo real para conclusão
9. **Tempos Mínimo e Máximo**: Valores extremos de tempo para conclusão
10. **Taxa de Conclusão**: Percentual de alunos que concluíram a defesa

## KPIs que Podem Ser Implementados com os Dados Atuais

Com base nos dados existentes em nosso CSV, podemos implementar parcialmente os seguintes KPIs da CAPES:

1. **PDO (Distribuição das Orientações)**: Pode ser calculado usando os campos `advisor_id` e `student_id` para determinar a distribuição das orientações entre os docentes.

2. **ORI (Intensidade de Formação)**: Pode ser parcialmente implementado com os dados disponíveis, contabilizando o número de mestres e doutores formados por docente.

3. **DPI_discente (Qualidade da Produção Discente)**: Pode ser parcialmente implementado com o campo `publications`, mas precisaria de dados adicionais sobre a qualidade das publicações (estratos Qualis).

## KPIs que Necessitam de Dados Adicionais

Os seguintes KPIs da CAPES necessitam de fontes de dados adicionais para serem implementados:

1. **FOR-H**: Requer o fator H dos docentes permanentes da plataforma SCOPUS/WebOfScience e informações sobre a data de obtenção do doutorado.
   - **Implementação sugerida**: Adicionar campos para `scopus_h_index` e `graduation_date` na tabela de docentes.

2. **FOR e FORDT**: Requer informações sobre quais docentes possuem bolsas PQ e DT do CNPq.
   - **Implementação sugerida**: Adicionar campos `cnpq_pq_scholarship` e `cnpq_dt_scholarship` (booleanos) na tabela de docentes.

3. **DED (Dedicação Exclusiva)**: Requer informações sobre a dedicação dos docentes ao programa.
   - **Implementação sugerida**: Adicionar campo `exclusive_dedication` (booleano) na tabela de docentes.

4. **D3A (Docentes Intensamente Envolvidos)**: Requer dados sobre disciplinas ministradas e produção relevante.
   - **Implementação sugerida**: Adicionar estrutura para registrar disciplinas ministradas por docente e ampliar dados de produção.

5. **ADE1 e ADE2 (Atividade de Docentes Externos)**: Requer identificação de docentes colaboradores/visitantes e disciplinas ministradas.
   - **Implementação sugerida**: Adicionar campo `professor_type` (permanente/colaborador/visitante) e tabela de disciplinas.

6. **ATI, ATG1, ATG2 (Atividade Docente)**: Requer informações sobre disciplinas na pós-graduação, graduação e orientações de iniciação científica.
   - **Implementação sugerida**: Adicionar tabelas para disciplinas e orientações de IC.

7. **DPI_docente**: Requer informações detalhadas sobre publicações e suas classificações Qualis.
   - **Implementação sugerida**: Expandir o modelo de dados de publicações para incluir classificação Qualis e outros metadados.

8. **DPD, DTD, ADER (Distribuição da Produção)**: Requer informações detalhadas sobre publicações, patentes e aderência à área.
   - **Implementação sugerida**: Criar estrutura para categorizar publicações por área e registrar patentes.

9. **DIEP, DIEG, DIER (Indicadores de Egressos)**: Requer acompanhamento dos egressos e suas atividades após a titulação.
   - **Implementação sugerida**: Criar tabela de egressos com campos para atuação profissional, localização e vínculo com pós-graduação.

10. **DISC (Oferta de Disciplinas)**: Requer informações sobre disciplinas cadastradas e efetivamente ofertadas.
    - **Implementação sugerida**: Criar estrutura de dados para cadastro e oferta de disciplinas.

## Recomendações para Implementação

Para implementar os KPIs adicionais, recomendamos:

1. **Ampliar o Modelo de Dados**: Criar tabelas adicionais para armazenar informações sobre:
   - Disciplinas (ministradas na graduação e pós-graduação)
   - Publicações (com classificação Qualis)
   - Patentes e produções técnicas
   - Bolsas e financiamentos
   - Acompanhamento de egressos

2. **Integração com APIs Externas**: Desenvolver integrações com:
   - Plataforma Lattes/CNPq (para dados de currículos)
   - SCOPUS/Web of Science (para métricas de citação)
   - Plataforma Sucupira (para dados oficiais da CAPES)

3. **Implementação por Fases**:
   - **Fase 1**: Implementar KPIs que podem ser calculados com dados atuais
   - **Fase 2**: Adicionar campos para apoiar KPIs relacionados a docentes (FOR-H, FOR, FORDT, DED)
   - **Fase 3**: Implementar estrutura para disciplinas e produções técnicas
   - **Fase 4**: Desenvolver sistema de acompanhamento de egressos

## Próximos Passos

1. Revisar o modelo de dados atual e planejar as extensões necessárias
2. Implementar os novos campos e tabelas no banco de dados
3. Desenvolver interfaces para importação de dados adicionais (CSV, API, etc.)
4. Atualizar o dashboard para exibir os novos KPIs

---

**Observação**: Os KPIs CAPES são ferramentas quantitativas que subsidiam a avaliação qualitativa realizada pela Comissão de Área. A implementação completa desses indicadores permitirá uma autoavaliação mais precisa do programa de pós-graduação, facilitando o planejamento estratégico e a melhoria contínua.