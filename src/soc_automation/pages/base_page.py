from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..core.logger import get_logger
from ..handlers.modal_handler import ModalHandler


class BasePage:
    """Classe base para todas as páginas."""
    
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver
        self.logger = get_logger(__name__)
        self.wait = WebDriverWait(driver, 10)
        self.modal_handler = ModalHandler(driver)
    
    def find_element(self, locator):
        """Encontra um elemento com espera."""
        return self.wait.until(EC.presence_of_element_located(locator))
    
    def find_elements(self, locator):
        """Encontra múltiplos elementos com espera."""
        return self.wait.until(EC.presence_of_all_elements_located(locator))
    
    def click(self, locator):
        """Clica em um elemento com espera."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
    
    def input_text(self, locator, text):
        """Insere texto em um elemento."""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
    
    def check_modal(self) -> None:
        """Verifica e trata modais em qualquer página."""
        self.modal_handler.check_and_handle_modal()
    
    def switch_to_default_frame(self) -> None:
        """Muda para o frame padrão."""
        self.driver.switch_to.default_content()
    
    def switch_to_soc_frame(self) -> None:
        """Muda para o frame socframe."""
        self.wait.until(EC.frame_to_be_available_and_switch_to_it("socframe"))
    
    def navigate_to_screen(self, screen_code: str) -> None:
        """Navega para uma tela específica usando JavaScript."""
        self.switch_to_default_frame()
        self.driver.execute_script(screen_code)
        self.logger.info(f"Navegando para tela: {screen_code}")
    
    def get_current_screen_info(self) -> tuple[str, str]:
        """Obtém informações da tela atual."""
        try:
            screen_element = self.find_element((By.ID, "infoPrograma"))
            company_element = self.find_element((By.ID, "infoEmpresa"))
            return screen_element.text, company_element.text
        except:
            return "", ""