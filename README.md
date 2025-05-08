# SOC Automation Framework

Framework de automação Selenium para o Sistema SOC (sistema.soc.com.br/WebSoc).

## Visão Geral

Este framework simplifica a automação de tarefas no Sistema SOC, gerenciando:
- Login automático
- Navegação entre telas
- Troca de empresas
- Tratamento de modais/alertas
- Operações específicas como transferência de funcionários

## Estrutura

```
soc_automation_framework/
├── src/
│   └── soc_automation/
│       ├── core/            # Gerenciamento do driver e browser
│       ├── pages/           # Implementação de páginas específicas
│       ├── handlers/        # Tratamento de modais e diálogos
│       ├── operations/      # Operações de negócio (ex: transferência)
│       └── utils/           # Funções auxiliares
```

## Funcionalidades Implementadas

- **Gerenciamento de driver**: Download e configuração automática do ChromeDriver
- **Tratamento de contexto**: Gerenciamento automático de frames e janelas
- **Login**: Login com verificação de sucesso e tratamento de erros
- **Navegação**: Mudança de telas via códigos numéricos
- **Troca de empresa**: Navegação entre empresas diferentes
- **Transferência de funcionário**: Processo completo de busca e transferência

## Como Usar

### Instalação

```bash
pip install -e .
```

### Exemplo de Uso Básico

```python
from soc_automation_framework.src.soc_automation.core.browser import Browser

# Inicializa o navegador
browser = Browser(headless=False)

try:
    # Login no sistema
    browser.login("seu_usuario", "sua_senha", "id_empresa")
    
    # Obter página home
    home = browser.get_home_page()
    
    # Navegar para tela específica (por número)
    home.navigate_to_screen_by_number("232")  # Tela de funcionários
    
    # Trocar de empresa
    home.change_company("547850")
    
    input("Pressione Enter para fechar...")
    
finally:
    browser.quit()
```

### Exemplo: Transferência de Funcionário

```python
# Inicializar browser
browser = Browser()

# Login no sistema
browser.login("usuario", "senha", "id")

# Acessar operações de funcionário
func_ops = browser.get_funcionario_operations()

# Configurar e executar transferência
resultado = func_ops.transferir(
    termo_busca="846.872.660-59",    # CPF, código ou nome
    tipo_busca="cpf",                # Tipo de busca
    empresa_origem="143906",         # Empresa atual
    empresa_destino="2498",          # Empresa destino
    filtros={"ativo": False, "inativo": True}  # Filtros opcionais
)

if resultado:
    print("✅ Transferência realizada com sucesso!")
```

## Características Principais

- **Detecção automática de modais**: Tratamento automático de alertas e diálogos
- **Resiliência**: Múltiplas tentativas em operações críticas e tratamento robusto de erros
- **Logging detalhado**: Registro completo de cada etapa e possíveis falhas
- **Gerenciamento de contexto**: Recuperação automática de contexto em caso de erros

## Requisitos

- Python 3.8+
- Selenium 4.0+
- WebDriver Manager 4.0+
- Google Chrome

## Próximos Passos

- Implementar operações adicionais (cadastro, edição, etc)
- Criar mecanismo de relatórios
- Adicionar suporte a múltiplos browsers
