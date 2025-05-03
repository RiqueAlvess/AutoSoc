from typing import Optional

from selenium import webdriver

from .driver_manager import DriverManager
from .logger import get_logger
from ..pages.login_page import LoginPage
from ..pages.home_page import HomePage


class Browser:
    """Classe principal para gerenciar o navegador."""
    
    def __init__(self, headless: bool = False) -> None:
        self.logger = get_logger(__name__)
        self.driver_manager = DriverManager()
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
    
    def start(self) -> webdriver.Chrome:
        """Inicia o navegador."""
        if not self.driver:
            self.driver = self.driver_manager.create_driver(self.headless)
            self.logger.info("Navegador iniciado")
        return self.driver
    
    def quit(self) -> None:
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("Navegador fechado")
    
    def navigate_to(self, url: str) -> None:
        """Navega para uma URL específica."""
        if not self.driver:
            self.start()
        
        self.driver.get(url)
        self.logger.info(f"Navegando para: {url}")
    
    def navigate_to_soc(self) -> None:
        """Navega para o sistema SOC."""
        self.navigate_to("https://sistema.soc.com.br/WebSoc/")
    
    def login(self, username: str, password: str, company_id: str) -> bool:
        """Realiza login no sistema SOC.
        
        Args:
            username: Nome de usuário
            password: Senha
            company_id: ID da empresa
            
        Returns:
            bool: True se login bem sucedido, False caso contrário
        """
        if not self.driver:
            self.start()
        
        self.navigate_to_soc()
        login_page = LoginPage(self.driver)
        return login_page.login(username, password, company_id)
    
    def get_home_page(self) -> HomePage:
        """Retorna instância da página home."""
        if not self.driver:
            self.start()
        return HomePage(self.driver)