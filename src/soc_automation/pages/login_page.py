from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage
from ..handlers.modal_handler import ModalHandler
from ..core.logger import get_logger


class LoginPage(BasePage):
    """Página de login do sistema SOC."""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.logger = get_logger(__name__)
        self.modal_handler = ModalHandler(driver)
    
    def fill_credentials(self, username: str, password: str, company_id: str) -> None:
        """Preenche as credenciais usando JavaScript."""
        script = """
        document.getElementById('usu').value = arguments[0];
        document.getElementById('senha').value = arguments[1];
        document.getElementById('empsoc').value = arguments[2];
        """
        self.driver.execute_script(script, username, password, company_id)
        
    def click_login_button(self) -> None:
        """Clica no botão de login usando JavaScript."""
        script = "document.getElementById('bt_entrar').click();"
        self.driver.execute_script(script)
    
    def verify_login_success(self) -> bool:
        """Verifica se o login foi bem sucedido."""
        try:
            # Aguarda a barra aparecer
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "barra"))
            )
            # Verifica elementos adicionais para confirmar
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "barraIcones"))
            )
            return True
        except TimeoutException:
            return False
    
    def login(self, username: str, password: str, company_id: str, max_attempts: int = 2) -> bool:
        """Realiza o login com tratamento de erros.
        
        Args:
            username: Nome de usuário
            password: Senha
            company_id: ID da empresa
            max_attempts: Número máximo de tentativas (padrão: 2)
            
        Returns:
            bool: True se login bem sucedido, False caso contrário
        """
        for attempt in range(1, max_attempts + 1):
            self.logger.info(f"Tentativa de login {attempt}/{max_attempts}")
            
            self.fill_credentials(username, password, company_id)
            self.click_login_button()
            
            # Verifica se apareceu modal de erro
            modal_found, message = self.modal_handler.check_and_handle_modal()
            
            if modal_found:
                if "incorreto" in message.lower() or "senha" in message.lower():
                    self.logger.error(f"Erro de credenciais: {message}")
                    if attempt == max_attempts:
                        self.logger.error("Limite de tentativas atingido. Parando para evitar bloqueio.")
                        return False
                    continue
                else:
                    self.logger.warning(f"Alerta do sistema: {message}")
            
            # Verifica se login foi bem sucedido
            if self.verify_login_success():
                self.logger.info("Login realizado com sucesso!")
                return True
                
        return False