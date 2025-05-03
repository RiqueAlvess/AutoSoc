import subprocess
import sys
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from .logger import get_logger


class DriverManager:
    """Gerencia a inicialização e configuração do WebDriver."""
    
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self._ensure_dependencies()
    
    def _ensure_dependencies(self) -> None:
        """Garante que as dependências estão instaladas e atualizadas."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "selenium"]
            )
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"]
            )
            self.logger.info("Dependências atualizadas com sucesso")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao atualizar dependências: {e}")
            raise
    
    def create_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Cria e configura uma instância do ChromeDriver.
        
        Args:
            headless: Se True, executa o navegador em modo headless.
            
        Returns:
            Uma instância configurada do ChromeDriver.
        """
        options = self._get_chrome_options(headless)
        
        try:
            # Usa o ChromeDriverManager para baixar e usar a versão correta
            driver_path = ChromeDriverManager().install()
            service = ChromeService(executable_path=driver_path)
            
            driver = webdriver.Chrome(service=service, options=options)
            self.logger.info("ChromeDriver inicializado com sucesso")
            return driver
            
        except Exception as e:
            self.logger.error(f"Erro ao criar ChromeDriver: {e}")
            raise
    
    def _get_chrome_options(self, headless: bool) -> ChromeOptions:
        """Configura as opções do Chrome.
        
        Args:
            headless: Se True, configura o modo headless.
            
        Returns:
            Objeto ChromeOptions configurado.
        """
        options = ChromeOptions()
        
        # Configurações básicas
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Previne detecção de automação
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        if headless:
            options.add_argument("--headless")
            
        return options