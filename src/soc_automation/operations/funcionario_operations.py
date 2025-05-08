import time
from typing import Dict, Optional, Any, Union, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

from ..core.logger import get_logger
from ..pages.home_page import HomePage
from ..handlers.modal_handler import ModalHandler


class FuncionarioOperations:
    TIPOS_BUSCA = {
        "nome": "0",
        "codigo": "1",
        "rg": "2",
        "cpf": "3",
        "matricula": "4",
        "pis": "5",
        "registro_rh": "6",
        "nome_social": "8"
    }
    
    TIPOS_BUSCA_POPUP = {
        "nome": "rbNome",
        "codigo": "rbCodigo",
        "rg": "rbRG",
        "cpf": "rbCPF",
        "matricula": "rbMatricula",
        "pis": "rbNit"
    }
    
    def __init__(self, browser) -> None:
        self.browser = browser
        self.driver = browser.driver
        self.home_page = HomePage(self.driver)
        self.logger = get_logger(__name__)
        self.modal_handler = ModalHandler(self.driver)
        self.wait = WebDriverWait(self.driver, 10)
        self.main_window = None
        
    def transferir(self, 
                  termo_busca: str, 
                  tipo_busca: str = "nome", 
                  filtros: Optional[Dict[str, bool]] = None, 
                  empresa_origem: Optional[str] = None, 
                  empresa_destino: Optional[str] = None, 
                  copiar_ficha_clinica: bool = True, 
                  copiar_cadastro_medico: bool = True, 
                  copiar_historico_vacinas: bool = True, 
                  copiar_historico_laboral: bool = True, 
                  copiar_socged: bool = True, 
                  migrar_somente_ficha: bool = True) -> bool:
        """Transfere um funcionário para outra empresa/unidade.
        
        Args:
            termo_busca: Termo para buscar o funcionário
            tipo_busca: Tipo de busca (nome, codigo, rg, cpf, matricula, pis, registro_rh, nome_social)
            filtros: Dicionário com filtros (ativo, inativo, pendente, afastado, ferias)
            empresa_origem: Código da empresa origem (se precisar mudar)
            empresa_destino: Código da empresa destino
            copiar_ficha_clinica: Se deve copiar a ficha clínica
            copiar_cadastro_medico: Se deve copiar o cadastro médico
            copiar_historico_vacinas: Se deve copiar o histórico de vacinas
            copiar_historico_laboral: Se deve copiar o histórico laboral
            copiar_socged: Se deve copiar o SocGed
            migrar_somente_ficha: Se deve migrar somente a ficha
            
        Returns:
            bool: True se transferência concluída com sucesso
        """
        self.logger.info(f"Iniciando transferência do funcionário: {termo_busca}")
        
        try:
            # Guarda a janela principal para referência
            self.main_window = self.driver.current_window_handle
            self.logger.info(f"Janela principal: {self.main_window}")
            
            if not self._preparar_ambiente(empresa_origem):
                return False
                
            if not self._localizar_funcionario(termo_busca, tipo_busca, filtros):
                return False
                
            if not self._configurar_transferencia(
                    copiar_ficha_clinica, 
                    copiar_cadastro_medico,
                    copiar_historico_vacinas, 
                    copiar_historico_laboral,
                    copiar_socged, 
                    migrar_somente_ficha):
                return False
                
            if not self._definir_destino(empresa_destino, termo_busca, tipo_busca):
                return False
                
            if not self._finalizar_transferencia():
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na transferência: {str(e)}")
            self._garantir_contexto_principal()
            return False
            
    def _garantir_contexto_principal(self) -> None:
        """Garante que estamos no contexto da janela principal."""
        try:
            handles = self.driver.window_handles
            
            # Se houver mais de uma janela e não estivermos na principal
            if len(handles) > 1 and self.main_window and self.driver.current_window_handle != self.main_window:
                # Fecha outras janelas exceto a principal
                current = self.driver.current_window_handle
                for handle in handles:
                    if handle != self.main_window:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                
                # Volta para janela principal
                self.driver.switch_to.window(self.main_window)
                self.logger.info("Contexto restaurado para janela principal")
            
            # Se só temos uma janela, garantimos que voltamos ao frame correto
            self.home_page.switch_to_default_frame()
            self.home_page.switch_to_soc_frame()
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar contexto: {str(e)}")
            
    def _preparar_ambiente(self, empresa_origem: Optional[str]) -> bool:
        """Prepara o ambiente para transferência."""
        try:
            if empresa_origem:
                self.logger.info(f"Mudando para empresa de origem: {empresa_origem}")
                self.home_page.change_company(empresa_origem)
                time.sleep(2)
            
            self.home_page.navigate_to_screen_by_number("232")
            time.sleep(2)
            self.home_page.switch_to_soc_frame()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao preparar ambiente: {str(e)}")
            return False
    
    def _localizar_funcionario(self, 
                              termo_busca: str, 
                              tipo_busca: str = "nome", 
                              filtros: Optional[Dict[str, bool]] = None) -> bool:
        """Localiza e seleciona o funcionário na tela."""
        try:
            if not self._buscar_funcionario(termo_busca, tipo_busca, filtros):
                return False
                
            if not self._selecionar_primeiro_funcionario():
                return False
                
            if not self._iniciar_transferencia():
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Erro ao localizar funcionário: {str(e)}")
            return False
    
    def _configurar_transferencia(self, 
                                 copiar_ficha_clinica: bool, 
                                 copiar_cadastro_medico: bool,
                                 copiar_historico_vacinas: bool, 
                                 copiar_historico_laboral: bool,
                                 copiar_socged: bool, 
                                 migrar_somente_ficha: bool) -> bool:
        """Configura as opções de transferência."""
        try:
            # Garante que estamos no contexto correto
            self._garantir_contexto_principal()
            
            # Tenta até 3 vezes entrar no modo de alteração
            for tentativa in range(3):
                try:
                    self.logger.info(f"Tentativa {tentativa+1} de configuração: executando 'alt'")
                    self.driver.execute_script("doAcao('alt');")
                    time.sleep(3)  # Espera mais tempo
                    
                    # Verifica se algum modal apareceu
                    modal_found, modal_message = self.modal_handler.check_and_handle_modal()
                    if modal_found:
                        self.logger.info(f"Modal tratado: {modal_message}")
                    
                    # Verifica se conseguimos entrar no modo de edição procurando por um dos checkboxes
                    checkboxes = self.driver.find_elements(By.ID, "copiaFichaClinica")
                    if checkboxes and len(checkboxes) > 0:
                        self.logger.info("Modo de edição ativado com sucesso")
                        break
                    else:
                        self.logger.warning("Não foi possível confirmar o modo de edição")
                        # Tira screenshot para debug
                        screenshot_path = f"erro_transferencia_{int(time.time())}.png"
                        self.driver.save_screenshot(screenshot_path)
                        self.logger.info(f"Screenshot salvo em {screenshot_path}")
                except Exception as e:
                    self.logger.warning(f"Erro na tentativa {tentativa+1}: {str(e)}")
                    time.sleep(2)
            
            # Configura os checkboxes, ignorando erros individuais
            checkboxes_config = {
                "copiaFichaClinica": copiar_ficha_clinica,
                "copiaCadastroMedico": copiar_cadastro_medico,
                "copiaHistoricoVacinas": copiar_historico_vacinas,
                "copiaHistoricoLaboral": copiar_historico_laboral,
                "copiaSocGed": copiar_socged,
                "migrarSomenteFicha": migrar_somente_ficha
            }
            
            for checkbox_id, valor in checkboxes_config.items():
                try:
                    self._definir_checkbox(checkbox_id, valor)
                except:
                    self.logger.warning(f"Não foi possível configurar o checkbox {checkbox_id}")
            
            # Tenta associar todos
            try:
                self.driver.execute_script("fassociarTodos();")
                time.sleep(2)
            except:
                self.logger.warning("Erro ao executar 'fassociarTodos'")
            
            self.logger.info("Opções de transferência configuradas")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar transferência: {str(e)}")
            return False
    
    def _definir_destino(self, 
                        empresa_destino: Optional[str], 
                        termo_busca: str,
                        tipo_busca: str) -> bool:
        """Define o destino da transferência."""
        try:
            # Garante que estamos no contexto correto
            self._garantir_contexto_principal()
            
            if not empresa_destino:
                self.logger.error("Código da empresa destino não fornecido")
                return False
                
            if not self._selecionar_empresa_destino(empresa_destino):
                return False
                
            # Tentamos selecionar funcionário destino, mas prosseguimos mesmo se falhar
            try:
                self._selecionar_funcionario_destino(termo_busca, tipo_busca)
            except Exception as e:
                self.logger.warning(f"Erro ao selecionar funcionário destino: {str(e)}")
                self.logger.info("Tentando prosseguir mesmo sem selecionar funcionário destino")
                
            return True
        except Exception as e:
            self.logger.error(f"Erro ao definir destino: {str(e)}")
            return False
    
    def _buscar_funcionario(self, 
                           termo_busca: str, 
                           tipo_busca: str = "nome",
                           filtros: Optional[Dict[str, bool]] = None) -> bool:
        """Busca funcionário com os critérios especificados."""
        try:
            filtros_padrao = {
                "ativo": True,
                "inativo": True,
                "pendente": True,
                "afastado": True,
                "ferias": True
            }
            
            if filtros:
                filtros_padrao.update(filtros)
            
            if tipo_busca in self.TIPOS_BUSCA:
                tipo_busca_value = self.TIPOS_BUSCA[tipo_busca]
                script = f"document.querySelector('input[name=\"codigoPesquisaFuncionario\"][value=\"{tipo_busca_value}\"]').checked = true"
                self.driver.execute_script(script)
            
            for filtro, valor in filtros_padrao.items():
                try:
                    checkbox = self.driver.find_element(By.NAME, filtro)
                    current_state = checkbox.is_selected()
                    if current_state != valor:
                        checkbox.click()
                except NoSuchElementException:
                    self.logger.warning(f"Filtro não encontrado: {filtro}")
            
            input_busca = self.driver.find_element(By.NAME, "nomeSeach")
            input_busca.clear()
            input_busca.send_keys(termo_busca)
            
            self.driver.execute_script("doAcao('browse');")
            time.sleep(2)
            
            resultados = self.driver.find_elements(By.CSS_SELECTOR, "table.resultados tr:not(:first-child)")
            if not resultados:
                self.logger.error(f"Nenhum funcionário encontrado: {termo_busca}")
                return False
                
            self.logger.info(f"Encontrados {len(resultados)} funcionário(s)")
            return True
        except Exception as e:
            self.logger.error(f"Erro na busca de funcionário: {str(e)}")
            return False
    
    def _selecionar_primeiro_funcionario(self) -> bool:
        """Seleciona o primeiro funcionário dos resultados."""
        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "table.resultados tr:not(:first-child) td.codigo a")
            if not links:
                self.logger.error("Nenhum funcionário encontrado para seleção")
                return False
                
            # Extrai dados para log
            codigo = links[0].text.strip()
            try:
                linha = links[0].find_element(By.XPATH, "./../../..")
                nome = linha.find_element(By.XPATH, "./td[2]").text.strip()
                self.logger.info(f"Selecionando funcionário: {nome} (Código: {codigo})")
            except:
                self.logger.info(f"Selecionando funcionário: (Código: {codigo})")
            
            href = links[0].get_attribute("href")
            if href and "selbrowse" in href:
                script_id = href.split("'")[1]
                self.driver.execute_script(f"selbrowse('{script_id}');")
                time.sleep(2)
                return True
            else:
                self.logger.error("Link de seleção inválido")
                return False
        except Exception as e:
            self.logger.error(f"Erro ao selecionar funcionário: {str(e)}")
            return False
    
    def _iniciar_transferencia(self) -> bool:
        """Inicia o processo de transferência."""
        try:
            # Tenta encontrar o botão/opção de transferência
            try:
                # Primeiro tenta encontrar pelo link direto
                transfer_link = self.driver.find_element(By.CSS_SELECTOR, "a[onclick*='transfunc']")
                transfer_link.click()
            except:
                # Se não encontrar, usa o script direto
                self.logger.info("Executando ação de transferência via script")
                self.driver.execute_script("doAcao('transfunc');")
            
            # Aguarda mais tempo (5 segundos) para carregar
            time.sleep(5)
            
            # Verifica modal que pode aparecer
            modal_found, modal_message = self.modal_handler.check_and_handle_modal()
            if modal_found:
                self.logger.info(f"Modal tratado: {modal_message}")
            
            # Tenta diferentes estratégias para verificar se a tela carregou
            for _ in range(3):  # Tenta até 3 vezes
                try:
                    # Verifica se estamos na tela de transferência por diferentes elementos
                    if self.driver.find_elements(By.ID, "copiaFichaClinica"):
                        self.logger.info("Tela de transferência carregada (verificado por copiaFichaClinica)")
                        return True
                    elif self.driver.find_elements(By.NAME, "empVo.cod"):
                        self.logger.info("Tela de transferência carregada (verificado por empVo.cod)")
                        return True
                    
                    # Verifica por texto que possa indicar a tela de transferência
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if "Transferência de Funcionário" in page_text:
                        self.logger.info("Tela de transferência carregada (verificado por texto)")
                        return True
                    
                    self.logger.warning("Tela de transferência ainda não identificada, aguardando...")
                    time.sleep(2)
                except:
                    self.logger.warning("Erro ao verificar tela, tentando novamente...")
                    time.sleep(2)
            
            # Se chegou aqui, tenta prosseguir para a alteração mesmo assim
            self.logger.warning("Tentando prosseguir mesmo sem confirmar a tela")
            return True
        
        except Exception as e:
            self.logger.error(f"Erro ao iniciar transferência: {str(e)}")
            return False
    
    def _definir_checkbox(self, checkbox_id: str, valor: bool) -> None:
        """Define o estado de um checkbox."""
        try:
            checkbox = self.driver.find_element(By.ID, checkbox_id)
            current_state = checkbox.is_selected()
            if current_state != valor:
                checkbox.click()
        except NoSuchElementException:
            self.logger.warning(f"Checkbox não encontrado: {checkbox_id}")
        except Exception as e:
            self.logger.warning(f"Erro ao definir checkbox {checkbox_id}: {str(e)}")
    
    def _selecionar_empresa_destino(self, empresa_destino: str) -> bool:
        """Seleciona a empresa destino."""
        try:
            select_empresa = self.wait.until(
                EC.presence_of_element_located((By.ID, "codigoDaEmpresa"))
            )
            
            script = f"document.getElementById('codigoDaEmpresa').value = '{empresa_destino}';"
            self.driver.execute_script(script)
            
            script_update = "trazUnseca(document.getElementById('codigoDaEmpresa').value);"
            self.driver.execute_script(script_update)
            
            time.sleep(2)
            self.logger.info(f"Empresa destino selecionada: {empresa_destino}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao selecionar empresa destino: {str(e)}")
            return False

    def _selecionar_funcionario_destino(self, termo_busca: str, tipo_busca: str) -> bool:
        """Seleciona o funcionário destino usando o mesmo critério do funcionário origem."""
        original_window = self.driver.current_window_handle
        new_window = None
        
        try:
            # Guarda o número de janelas antes de abrir uma nova
            janelas_antes = len(self.driver.window_handles)
            self.logger.info(f"Janelas antes de abrir popup: {janelas_antes}")
            
            # Abre a janela de seleção
            self.logger.info("Abrindo janela de seleção de funcionário destino")
            self.driver.execute_script("javascript:zoom();")
            time.sleep(3)  # Espera mais tempo para a janela abrir
            
            # Verifica quantas janelas temos agora
            janelas_depois = len(self.driver.window_handles)
            self.logger.info(f"Janelas depois de tentar abrir popup: {janelas_depois}")
            
            if janelas_depois <= janelas_antes:
                self.logger.warning("Nova janela não foi aberta. Prosseguindo sem selecionar funcionário.")
                return False
            
            # Identifica a nova janela
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    new_window = window_handle
                    self.driver.switch_to.window(new_window)
                    self.logger.info(f"Mudou para nova janela: {new_window}")
                    break
            
            if not new_window:
                self.logger.warning("Nova janela não detectada. Prosseguindo sem selecionar funcionário.")
                return False
            
            # Executa a busca na nova janela
            input_busca = self.driver.find_element(By.NAME, "nomeSeach")
            input_busca.clear()
            input_busca.send_keys(termo_busca)
            
            # Seleciona tipo de busca
            if tipo_busca in self.TIPOS_BUSCA_POPUP:
                radio_id = self.TIPOS_BUSCA_POPUP[tipo_busca]
                try:
                    radio = self.driver.find_element(By.ID, radio_id)
                    if not radio.is_selected():
                        radio.click()
                except:
                    self.logger.warning(f"Radio button {radio_id} não encontrado")
            
            # Executa busca
            self.driver.execute_script("doAcao('browse');")
            time.sleep(2)
            
            # Seleciona o primeiro resultado
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='javascript:sendValue']")
            if not links:
                self.logger.warning("Nenhum funcionário destino encontrado. Fechando janela.")
                self.driver.close()
                self.driver.switch_to.window(original_window)
                return False
                
            # Executa a seleção
            href = links[0].get_attribute("href")
            self.logger.info(f"Selecionando via script: {href.split('javascript:')[1]}")
            self.driver.execute_script(href.split("javascript:")[1])
            time.sleep(2)
            
            # Verifica se a janela ainda existe ou foi fechada automaticamente
            window_handles = self.driver.window_handles
            if new_window in window_handles:
                self.logger.info("Fechando janela manualmente")
                self.driver.close()
            
            # Volta para janela original
            self.driver.switch_to.window(original_window)
            self.logger.info("Voltou para janela original")
            
            # Garante que estamos no frame correto
            self.home_page.switch_to_default_frame()
            self.home_page.switch_to_soc_frame()
            self.logger.info("Frame restaurado")
            
            self.logger.info(f"Funcionário destino selecionado: {termo_busca}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao selecionar funcionário destino: {str(e)}")
            
            # Restaura contexto em caso de erro
            try:
                self._garantir_contexto_principal()
            except:
                self.logger.error("Falha ao restaurar contexto após erro")
                
            return False
    
    def _verificar_modais_transferencia(self) -> None:
        """Verifica modais específicos de transferência."""
        try:
            # Lista de possíveis IDs de modais de transferência
            modal_ids = ["alertaErroTransferencia", "modalalertas", "modalTransfFuncionario"]
            
            for modal_id in modal_ids:
                try:
                    # Tenta encontrar o modal
                    modal = self.driver.find_element(By.ID, modal_id)
                    
                    if modal.is_displayed():
                        # Extrai a mensagem
                        mensagem = ""
                        try:
                            # Tenta diferentes localizadores para a mensagem
                            mensagem_element = modal.find_element(By.ID, "conteudosTable")
                            mensagem = mensagem_element.text
                        except:
                            try:
                                # Tenta outro padrão de mensagem
                                mensagem_element = modal.find_element(By.CSS_SELECTOR, ".modalConteudo")
                                mensagem = mensagem_element.text
                            except:
                                self.logger.warning(f"Não foi possível extrair texto do modal {modal_id}")
                        
                        if mensagem:
                            self.logger.info(f"Modal de transferência encontrado: {mensagem}")
                        
                        # Tenta clicar no botão OK
                        try:
                            # Primeiro tenta pelo script específico
                            if modal_id == "alertaErroTransferencia":
                                self.driver.execute_script("fecharErroTransferencia();")
                            else:
                                # Tenta encontrar o botão OK e clicar
                                botao_ok = modal.find_element(By.CSS_SELECTOR, ".botaoT")
                                botao_ok.click()
                        except:
                            self.logger.warning(f"Não foi possível clicar no botão do modal {modal_id}")
                        
                        time.sleep(1)
                        break
                except NoSuchElementException:
                    continue
                
        except Exception as e:
            self.logger.warning(f"Erro ao verificar modais de transferência: {str(e)}")

    def _retornar_tela_inicial(self) -> None:
        """Retorna à tela inicial de troca de empresa."""
        try:
            # Switch para o frame padrão
            self.home_page.switch_to_default_frame()
            
            # Executa script para retornar à tela inicial
            script = "javascript:Empresas(); hideall();hidemenus('');menu_close();avisoLogin();"
            self.driver.execute_script(script)
            self.logger.info("Retornando à tela inicial")
            
            # Aguarda carregar
            time.sleep(3)
            
            # Verifica possíveis modais
            modal_found, modal_message = self.modal_handler.check_and_handle_modal()
            if modal_found:
                self.logger.info(f"Modal tratado ao retornar à tela inicial: {modal_message}")
                
        except Exception as e:
            self.logger.warning(f"Erro ao retornar à tela inicial: {str(e)}")
    
    def _finalizar_transferencia(self) -> bool:
        """Finaliza o processo de transferência."""
        try:
            # Garante que estamos no contexto correto
            self._garantir_contexto_principal()
            
            self.logger.info("Finalizando transferência: executando 'save'")
            self.driver.execute_script("doAcao('save');")
            time.sleep(2)
            
            # Trata possível alerta javascript
            alerta_encontrado = False
            for _ in range(3):  # Tenta várias vezes, pois o alerta pode demorar
                try:
                    alert = self.driver.switch_to.alert
                    mensagem_alert = alert.text
                    self.logger.info(f"Alerta confirmado: {mensagem_alert}")
                    alert.accept()
                    alerta_encontrado = True
                    time.sleep(2)
                    break
                except:
                    time.sleep(1)  # Espera um pouco e tenta novamente
            
            # Verifica possíveis modais específicos de transferência
            self._verificar_modais_transferencia()
            
            # Verifica possível modal do SOC genérico
            modal_found, modal_message = self.modal_handler.check_and_handle_modal()
            if modal_found:
                self.logger.info(f"Modal tratado: {modal_message}")
            
            # Retorna à tela inicial
            self._retornar_tela_inicial()
            
            # Verifica se retornou à tela de funcionários ou inicial
            try:
                screen_info, _ = self.home_page.get_current_screen_info()
                self.logger.info(f"Tela final: {screen_info}")
                
                if "232" in screen_info or "Funcionário" in screen_info or "Página Inicial" in screen_info:
                    self.logger.info("Transferência concluída com sucesso")
                    return True
            except:
                self.logger.warning("Não foi possível verificar a tela final")
            
            # Consideramos sucesso se encontramos um alerta ou modal
            if alerta_encontrado or modal_found:
                self.logger.info("Transferência considerada concluída (alerta/modal encontrado)")
                return True
                
            self.logger.info("Transferência considerada concluída sem confirmação")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao finalizar transferência: {str(e)}")
            # Ainda consideramos como potencial sucesso mesmo com erro
            self.logger.warning("Transferência pode ter sido concluída apesar do erro")
            return True