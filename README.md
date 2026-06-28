# Cardápio Nutricional — Técnico em Nutrição

Aplicativo desktop para montagem e avaliação de cardápios nutricionais com validação automática de macronutrientes. Desenvolvido para a ETEC Julio de Mesquita, turma Técnico em Nutrição.

---

## Funcionalidades

- Criação de cardápios com kcal total e distribuição por refeição
- Busca de alimentos da base TACO (com suporte a pesquisa sem acento)
- Adição de alimentos personalizados diretamente no cardápio (sem cadastrar no banco)
- Cálculo automático de macronutrientes em tempo real
- Validação visual se os macros estão dentro dos ranges recomendados
- Exportar e importar cardápios (para o professor avaliar os cardápios dos alunos)
- Gerenciamento de alimentos e grupos personalizados
- Importar / exportar alimentos via planilha Excel
- Template Excel para preenchimento e importação de alimentos sem erros de formatação
- Restauração da base TACO aos valores originais

---

## Estrutura do projeto

```
cardapio_nutricional/
├── main.py                        # Ponto de entrada — execute este arquivo
├── importar_taco.py               # Script alternativo de importação via terminal
├── requirements.txt
├── taco/
│   └── Taco.xlsx                  # Base TACO embutida (importada automaticamente)
├── database/
│   └── db.py                      # Conexão SQLite e criação das tabelas
├── models/
│   ├── modelos.py                 # Classes Alimento, Refeicao, Cardapio
│   └── repositorio.py             # Operações de banco de dados (CRUD)
└── views/
    ├── estilos.py                 # Paleta de cores e fontes
    ├── tela_home.py               # Tela 1 — Lista de cardápios
    ├── tela_configuracao.py       # Tela 2 — Nome, kcal e refeições
    ├── tela_montagem.py           # Tela 3 — Adição de alimentos e validação
    └── tela_gerenciar_alimentos.py  # Gerenciamento de alimentos e grupos
```

---

## Pré-requisitos

- Python 3.10 ou superior
- tkinter (incluso no Python padrão — verifique com `python -m tkinter`)

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Executar o aplicativo

```bash
python main.py
```

Na primeira execução, os alimentos da tabela TACO são importados automaticamente para o banco de dados.

---

## Banco de dados

O banco é criado automaticamente em:

- **Windows:** `C:\Users\<usuario>\AppData\Roaming\CardapioNutricional\cardapio.db`
- **Linux/Mac:** `~/.cardapio_nutricional/cardapio.db`

---

## Ranges de macronutrientes

| Macro        | % das kcal da refeição | Kcal/g |
|--------------|------------------------|--------|
| Carboidratos | 45% – 60%              | 4 kcal |
| Proteínas    | 10% – 20%              | 4 kcal |
| Lipídeos     | 20% – 30%              | 9 kcal |

Os valores da tabela TACO são referentes a **100g** do alimento. O cálculo é proporcional à quantidade em gramas informada.

---

## Exportar e importar cardápios

O professor pode receber os cardápios dos alunos em formato `.cardapio` e importá-los diretamente pelo aplicativo para avaliação.

**Aluno (exportar):**
1. Selecione o cardápio na tela inicial
2. Clique em **📤 Exportar**
3. Salve o arquivo `.cardapio` e envie ao professor

**Professor (importar):**
1. Clique em **📥 Importar** na tela inicial
2. Selecione o arquivo `.cardapio` recebido
3. O cardápio aparece na lista com todos os alimentos e macros preservados

> Alimentos não encontrados no banco do professor são importados como personalizados e exibidos com ✎ na montagem.

---

## Importar alimentos via planilha

Para cadastrar alimentos em lote:

1. Vá em **Ferramentas → Gerenciar Alimentos**
2. Clique em **📋 Template** para baixar a planilha modelo
3. Preencha a partir da linha 2 (as primeiras linhas são exemplos)
4. Clique em **📥 Importar** e selecione o arquivo preenchido

---

## Gerar executável (.exe / binário)

Para distribuir o aplicativo em computadores sem Python instalado, use o PyInstaller. O comando deve ser executado no sistema operacional de destino.

**Windows:**
```cmd
pip install pyinstaller
pyinstaller --onefile --windowed --name "CardapioNutricional" --add-data "taco/Taco.xlsx;taco" main.py
```

**Linux/Mac:**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "CardapioNutricional" --add-data "taco/Taco.xlsx:taco" main.py
```

O executável gerado fica em `dist/`. Basta distribuir esse único arquivo — sem precisar instalar Python ou qualquer dependência.

> Para disponibilizar no GitHub, acesse **Releases → Create a new release** e faça upload do executável gerado.


pyinstaller --clean --onefile --windowed --name "ProjetoTACO" --add-data "taco/Taco.xlsx;taco" --add-data "logo.ico;." --icon=logo.ico main.py
