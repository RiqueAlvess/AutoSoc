from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from ..core.logger import get_logger


class ModalHandler:
    """Handler para modais/alertas do sistema SOC."""
    
    def __init__(self, driver, timeout: int = 2):
        self.driver = driver
        self.logger = get_logger(__name__)
        self.wait = WebDriverWait(driver, timeout)
    
    def check_and_handle_modal(self) -> tuple[bool, str]:
        """Verifica e lida com modais de alerta.
        
        Returns:
            tuple[bool, str]: (modal_found, message)
        """
        try:
            modal = self.wait.until(
                EC.presence_of_element_located((By.ID, "modalalertas"))
            )
            
            # Pega a mensagem do modal
            message_element = modal.find_element(By.ID, "modalalertasConteudo")
            message = message_element.text
            
            self.logger.warning(f"Modal detectado: {message}")
            
            # Clica no botão OK
            ok_button = modal.find_element(By.ID, "btn_ok")
            ok_button.click()
            
            return True, message
            
        except TimeoutException:
            return False, ""