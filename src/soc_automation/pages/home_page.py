import re
from selenium.webdriver.common.by import By
from .base_page import BasePage
from ..core.logger import get_logger


class HomePage(BasePage):
    """Página inicial do sistema SOC."""
    
    def __init__(self, driver):
        super().__init__(driver)
        self.logger = get_logger(__name__)
    
    def navigate_to_screen_by_number(self, screen_number: str) -> bool:
        """Navega para uma tela pelo número e verifica se chegou corretamente."""
        self.switch_to_default_frame()
        
        # Busca o menu
        menu_items = self.driver.find_elements(By.XPATH, "//tr[contains(@onclick, 'MainJava')]")
        
        for item in menu_items:
            onclick = item.get_attribute("onclick")
            if onclick and f"'{screen_number}'" in onclick:
                self.driver.execute_script(onclick)
                self.logger.info(f"Navegando para tela {screen_number}")
                
                # Verifica se chegou na tela correta
                return self._verify_screen_navigation(screen_number)
        
        self.logger.error(f"Tela {screen_number} não encontrada")
        return False
    
    def _verify_screen_navigation(self, expected_number: str) -> bool:
        """Verifica se chegou na tela correta."""
        import time
        time.sleep(3) 
        
        try:
            screen_info, _ = self.get_current_screen_info()
            if screen_info.startswith(expected_number):
                self.logger.info(f"Navegação confirmada: {screen_info}")
                return True
            else:
                self.logger.error(f"Esperado tela {expected_number}, mas está em: {screen_info}")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar navegação: {e}")
            return False
    
    def change_company(self, company_id: str) -> None:
        """Troca de empresa."""
        self.go_to_main_screen()
        self.switch_to_soc_frame()
        script = f"javascript:choiceemp('{company_id}');"
        self.driver.execute_script(script)
        self.logger.info(f"Trocando para empresa ID: {company_id}")
        self.check_modal()
    
    def go_to_main_screen(self) -> None:
        """Volta para a tela principal."""
        self.switch_to_default_frame()
        script = "javascript:Empresas(); hideall();hidemenus('');menu_close();avisoLogin();"
        self.driver.execute_script(script)
        self.logger.info("Voltando para tela principal")