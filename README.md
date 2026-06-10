# Cardápio Nutricional — Técnico em Nutrição

Aplicativo desktop para montagem de cardápios nutricionais com validação de macronutrientes.

---

## Estrutura do projeto

```
cardapio_nutricional/
├── main.py                        # Ponto de entrada — execute este arquivo
├── importar_taco.py               # Script de importação da tabela TACO (rode uma vez)
├── requirements.txt
├── database/
│   └── db.py                      # Conexão SQLite e criação das tabelas
├── models/
│   ├── modelos.py                 # Classes Alimento, Refeicao, Cardapio
│   └── repositorio.py             # Operações de banco de dados (CRUD)
└── views/
    ├── estilos.py                 # Paleta de cores e fontes
    ├── tela_home.py               # Tela 1 — Lista de cardápios
    ├── tela_configuracao.py       # Tela 2 — Nome, kcal e refeições
    └── tela_montagem.py           # Tela 3 — Adição de alimentos e validação
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

## Passo 1 — Importar a tabela TACO

Execute **uma única vez** para popular o banco com os alimentos:

```bash
python importar_taco.py caminho/para/sua/taco.xlsx
```

O banco `cardapio.db` será criado automaticamente em:
- **Windows:** `C:\Users\<seu_usuario>\AppData\Roaming\CardapioNutricional\`
- **Linux/Mac:** `~/.cardapio_nutricional/`

---

## Passo 2 — Executar o aplicativo

```bash
python main.py
```

---

## Passo 3 — Gerar o .exe (Windows)

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --name "CardapioNutricional" main.py
```

O `.exe` será gerado na pasta `dist/`.

> **Importante:** Distribua o `.exe` junto com o arquivo `cardapio.db` já populado com a TACO.
> Na primeira execução em um computador novo, copie o `.db` para a pasta AppData do usuário,
> ou deixe o app criar um banco vazio e importe a TACO separadamente.

---

## Ranges de macronutrientes (fixos no sistema)

| Macro        | % das kcal da refeição | Kcal/g |
|--------------|------------------------|--------|
| Carboidratos | 45% – 60%              | 4 kcal |
| Proteínas    | 10% – 20%              | 4 kcal |
| Lipídeos     | 20% – 30%              | 9 kcal |

Os valores da tabela TACO são referentes a **100g** do alimento.
O cálculo é proporcional à quantidade em gramas informada pelo aluno.

---

## Roadmap V2

- Cadastro, edição e remoção de alimentos pelo usuário
- Importação e exportação de alimentos (CSV/XLSX)
- Cadastro de novos grupos alimentares
- Exportação do cardápio em PDF
- Micronutrientes (vitaminas e minerais)
