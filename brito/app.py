import sqlite3

# --- Configuração do Banco de Dados ---
def init_db():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    
    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    ''')
    
    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    ''')
    
    # Criar um usuário padrão se não existir
    try:
        cursor.execute("INSERT INTO clientes (nome, usuario, senha) VALUES (?, ?, ?)", 
                       ('Administrador', 'admin', 'admin123'))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    conn.close()

# --- Funções do Sistema ---

def cadastrar_cliente():
    nome = input("Nome completo: ")
    usuario = input("Nome de usuário: ")
    senha = input("Senha: ")
    
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome, usuario, senha) VALUES (?, ?, ?)", (nome, usuario, senha))
        conn.commit()
        print(f"\n✅ Cliente {nome} cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\n❌ Erro: Este nome de usuário já existe.")
    finally:
        conn.close()

def login():
    usuario = input("Usuário: ")
    senha = input("Senha: ")
    
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes WHERE usuario = ? AND senha = ?", (usuario, senha))
    user = cursor.fetchone()
    conn.close()
    return user # Retorna (id, nome) ou None

def cadastrar_produto():
    nome = input("Nome do produto: ")
    preco = float(input("Preço: "))
    estoque = int(input("Quantidade inicial em estoque: "))
    
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)", (nome, preco, estoque))
    conn.commit()
    conn.close()
    print(f"\n📦 Produto {nome} adicionado!")

def listar_produtos():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    
    print("\n--- ESTOQUE ATUAL ---")
    print(f"{'ID':<4} | {'Produto':<20} | {'Preço':<10} | {'Qtd':<5}")
    for p in produtos:
        print(f"{p[0]:<4} | {p[1]:<20} | R${p[2]:<8.2f} | {p[3]:<5}")
    return produtos

def realizar_venda(cliente_id):
    listar_produtos()
    try:
        prod_id = int(input("\nID do produto que deseja comprar: "))
        qtd = int(input("Quantidade: "))
        
        conn = sqlite3.connect('sistema_vendas.db')
        cursor = conn.cursor()
        
        # Verificar estoque
        cursor.execute("SELECT nome, estoque FROM produtos WHERE id = ?", (prod_id,))
        produto = cursor.fetchone()
        
        if produto and produto[1] >= qtd:
            # Atualizar estoque
            cursor.execute("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", (qtd, prod_id))
            # Registrar venda
            cursor.execute("INSERT INTO vendas (cliente_id, produto_id, quantidade) VALUES (?, ?, ?)", 
                           (cliente_id, prod_id, qtd))
            conn.commit()
            print(f"\n💰 Venda realizada! {qtd}x {produto[0]} debitado do estoque.")
        else:
            print("\n❌ Erro: Estoque insuficiente ou produto inexistente.")
    except ValueError:
        print("\n❌ Erro: Entrada inválida.")
    finally:
        conn.close()

def historico_vendas():
    conn = sqlite3.connect('sistema_vendas.db')
    cursor = conn.cursor()
    # Join para mostrar o nome do cliente e do produto
    query = '''
        SELECT v.id, c.nome, p.nome, v.quantidade 
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN produtos p ON v.produto_id = p.id
    '''
    cursor.execute(query)
    vendas = cursor.fetchall()
    conn.close()
    
    print("\n--- HISTÓRICO DE VENDAS ---")
    print(f"{'ID':<4} | {'Cliente':<15} | {'Produto':<15} | {'Qtd':<5}")
    for v in vendas:
        print(f"{v[0]:<4} | {v[1]:<15} | {v[2]:<15} | {v[3]:<5}")

# --- Loop Principal ---
def menu():
    init_db()
    while True:
        print("\n=== SISTEMA DE VENDAS 1.0 ===")
        print("1. Login")
        print("2. Cadastrar Cliente")
        print("0. Sair")
        opcao = input("Escolha: ")

        if opcao == '1':
            user = login()
            if user:
                print(f"\n👋 Bem-vindo, {user[1]}!")
                while True:
                    print(f"\n--- MENU LOGADO ({user[1]}) ---")
                    print("1. Cadastrar Produto")
                    print("2. Ver Estoque")
                    print("3. Realizar Venda")
                    print("4. Histórico de Vendas")
                    print("0. Logout")
                    sub_opcao = input("Escolha: ")
                    
                    if sub_opcao == '1': cadastrar_produto()
                    elif sub_opcao == '2': listar_produtos()
                    elif sub_opcao == '3': realizar_venda(user[0])
                    elif sub_opcao == '4': historico_vendas()
                    elif sub_opcao == '0': break
            else:
                print("\n❌ Usuário ou senha incorretos.")
        
        elif opcao == '2':
            cadastrar_cliente()
        elif opcao == '0':
            break

if __name__ == "__main__":
    menu()

 