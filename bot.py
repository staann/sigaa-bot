# type: ignore
# Selenium - Automatizando tarefas no navegador
from pathlib import Path
from time import sleep
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Chrome Options
# https://peter.sh/experiments/chromium-command-line-switches/
# Doc Selenium
# https://selenium-python.readthedocs.io/locating-elements.html

# Caminho para a raiz do projeto
ROOT_FOLDER = Path(__file__).parent
# Caminho para a pasta onde o chromedriver está
CHROME_DRIVER_PATH = ROOT_FOLDER / 'driver' / 'chromedriver.exe'

SENHA = '' #Substitua pela sua senha
MATRICULA = '' #Substitua pela sua matricula
DATA_NASCIMENTO = '' #Substitua pela sua data de nascimento (dia, mes, ano)(apenas numeros)
CPF = '' #Substitua pelo seu CPF (sem pontos e traços)

def make_chrome_browser(*options: str) -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)

    # chrome_options.add_argument('--headless')
    if options is not None:
        for option in options:
            chrome_options.add_argument(option)

    chrome_service = Service(
        executable_path=str(CHROME_DRIVER_PATH),
    )

    browser = webdriver.Chrome(
        service=chrome_service,
        options=chrome_options
    )

    return browser

def aguardar_botao_com_refresh(browser, refresh_interval=1):
    """
    Aguarda o botão ficar disponível, fazendo refresh da página periodicamente.
    Continua infinitamente até o botão ser encontrado.
    """
    attempt = 0
    
    while True:  # Loop infinito
        try:
            attempt += 1
            print(f"Tentativa {attempt} - Verificando disponibilidade do botão...")
            
            # Verifica se há erro na página antes de procurar o botão
            if verificar_e_reiniciar_se_erro(browser):
                print("Navegador foi fechado devido a erro. Saindo da função...")
                browser = None  # Define como None para indicar que foi fechado
                return False
            
            # Tenta encontrar o botão com timeout maior para sites lentos
            botao_selecionar_turma = WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable((By.ID, "form:selecionarTurma"))
            )
            
            # Se chegou aqui, o botão está disponível
            print("Botão 'Selecionar Turma' está disponível!")
            botao_selecionar_turma.click()
            print("Botão 'Selecionar Turma' clicado com sucesso!")
            return True
            
        except TimeoutException:
            print(f"Botão ainda não disponível. Fazendo refresh da página em {refresh_interval} segundos...")
            
            # Faz refresh da página
            browser.refresh()
            print("Página atualizada. Aguardando carregamento...")
            time.sleep(0.1)  # Aumentado para 5 segundos para sites lentos
            
            # Verifica se há erro após o refresh
            if verificar_e_reiniciar_se_erro(browser):
                print("Navegador foi fechado após refresh. Saindo da função...")
                browser = None  # Define como None para indicar que foi fechado
                return False
            
            # Tenta navegar novamente para a página de matrícula se necessário
            try:
                print("Navegando novamente para a página de matrícula...")
                elemento = WebDriverWait(browser, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@class='ThemeOfficeMainFolderText' and text()='Ensino']"))
                )
                elemento.click()
                
                elemento = WebDriverWait(browser, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//td[@class='ThemeOfficeMenuFolderText' and contains(text(), 'Matrícula On-Line')]"))
                )
                elemento.click()
                
                elemento = WebDriverWait(browser, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//td[@class='ThemeOfficeMenuItemText' and contains(text(), 'Realizar Matrícula Extraordinária')]"))
                )
                elemento.click()
                
                # Preenche novamente o nome da matéria
                print("Preenchendo novamente o nome da matéria...")
                botao_nome_materia = WebDriverWait(browser, 3).until(EC.element_to_be_clickable((By.ID, 'form:txtNome')))
                botao_nome_materia.click()
                search_input_nome_materia = WebDriverWait(browser, 3).until(
                    EC.presence_of_element_located((By.ID, 'form:txtNome'))
                )
                search_input_nome_materia.send_keys('INTRODUÇÃO À UNB-ECO')
                search_input_nome_materia.send_keys(Keys.ENTER)
                print("Nome da matéria preenchido novamente com sucesso!")
                
                # Verifica se há erro após preencher novamente
                if verificar_e_reiniciar_se_erro(browser):
                    print("Navegador foi fechado após preencher matéria novamente. Saindo da função...")
                    browser = None  # Define como None para indicar que foi fechado
                    return False
                
            except Exception as nav_error:
                print(f"Erro ao navegar após refresh: {nav_error}")
                print("Continuando para próxima tentativa...")
                continue
            
            time.sleep(refresh_interval)
    
    return False

def detectar_pagina_erro(browser):
    """
    Detecta se a página atual é uma página de erro do site.
    Retorna True se for uma página de erro, False caso contrário.
    """
    try:
        # Verifica se há mensagens de erro comuns
        error_indicators = [
            "//div[contains(text(), 'Erro')]",
            "//div[contains(text(), 'Error')]",
            "//div[contains(text(), 'Falha')]",
            "//div[contains(text(), 'Problema')]",
            "//div[contains(text(), 'Sistema indisponível')]",
            "//div[contains(text(), 'Serviço temporariamente indisponível')]",
            "//div[contains(text(), 'Timeout')]",
            "//div[contains(text(), 'Sessão expirada')]",
            "//div[contains(text(), 'Acesso negado')]",
            "//div[contains(text(), 'Acesso bloqueado')]",
            "//div[contains(text(), 'Acesso restrito')]",
            "//div[contains(text(), 'Acesso não autorizado')]",
            "//div[contains(text(), 'Usuário não autorizado')]",
            "//div[contains(text(), 'Credenciais inválidas')]",
            "//div[contains(text(), 'Login falhou')]",
            "//div[contains(text(), 'Falha na autenticação')]",
            "//div[contains(text(), 'Página não encontrada')]",
            "//div[contains(text(), '404')]",
            "//div[contains(text(), '500')]",
            "//div[contains(text(), '503')]",
            "//div[contains(@class, 'error')]",
            "//div[contains(@class, 'Error')]",
            "//span[contains(text(), 'Erro')]",
            "//span[contains(text(), 'Error')]",
            "//span[contains(text(), 'Acesso negado')]",
            "//span[contains(text(), 'Acesso bloqueado')]",
            "//p[contains(text(), 'Erro')]",
            "//p[contains(text(), 'Error')]",
            "//p[contains(text(), 'Acesso negado')]",
            "//p[contains(text(), 'Acesso bloqueado')]"
        ]
        
        for indicator in error_indicators:
            try:
                error_element = browser.find_element(By.XPATH, indicator)
                if error_element.is_displayed():
                    print(f"Página de erro detectada: {error_element.text}")
                    return True
            except:
                continue
        
        # Verifica se a URL contém indicadores de erro
        current_url = browser.current_url
        error_urls = ['error', 'erro', 'fail', 'falha', 'timeout', 'expired', 'denied', 'blocked', 'restricted', 'unauthorized', 'invalid', '404', '500', '503']
        
        for error_term in error_urls:
            if error_term.lower() in current_url.lower():
                print(f"URL de erro detectada: {current_url}")
                return True
        
        # Verifica se o título da página indica erro
        page_title = browser.title.lower()
        error_titles = ['erro', 'error', 'falha', 'fail', 'problema', 'problem', 'indisponível', 'unavailable', 'negado', 'bloqueado', 'restrito', 'não autorizado', 'inválido']
        
        for error_term in error_titles:
            if error_term in page_title:
                print(f"Título de erro detectado: {browser.title}")
                return True
        
        return False
        
    except Exception as e:
        print(f"Erro ao verificar página de erro: {e}")
        return False

def verificar_e_reiniciar_se_erro(browser):
    """
    Verifica se há erro na página e reinicia o navegador se necessário.
    Retorna True se reiniciou, False se não há erro.
    """
    if detectar_pagina_erro(browser):
        print("Página de erro detectada! Fechando navegador...")
        try:
            browser.quit()
            print("Navegador fechado com sucesso.")
            # Aguarda um pouco para garantir que o processo seja finalizado
            time.sleep(0.2)
        except Exception as e:
            print(f"Erro ao fechar navegador: {e}")
            # Tenta fechar forçadamente
            try:
                browser.close()
            except:
                pass
        # Define o browser como None para indicar que foi fechado
        browser = None
        return True
    return False

def main():
    browser = None
    try:
        # código principal
        TIME_TO_WAIT = 0.1

        options = ()
        browser = make_chrome_browser(*options)

        print("Acessando página de login...")
        browser.get('https://autenticacao.unb.br/sso-server/login?service=https://sig.unb.br/sigaa/login/cas')

        print("Aguardando campos de login carregarem...")
        search_input_username = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located(
                (By.NAME, 'username')
            )
        )

        search_input_password = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located(
                (By.NAME, 'password')
            )
        )

        print("Preenchendo credenciais...")
        search_input_username.send_keys(MATRICULA)
        search_input_password.send_keys(SENHA)
        search_input_password.send_keys(Keys.ENTER)

        # Aguarda um pouco para o login processar
        time.sleep(0.1)
        
        # Verifica se o login foi bem-sucedido (procura por elementos que só aparecem após login)
        try:
            print("Verificando se o login foi bem-sucedido...")
            WebDriverWait(browser, 0.2).until(
                EC.presence_of_element_located((By.XPATH, "//span[@class='ThemeOfficeMainFolderText' and text()='Ensino']"))
            )
            print("Login realizado com sucesso!")
        except TimeoutException:
            raise Exception("Login falhou - não foi possível acessar o menu principal após o login")

        # Verifica se há erro na página após login
        if verificar_e_reiniciar_se_erro(browser):
            print("Navegador foi fechado devido a erro. Saindo da função...")
            return False, None

        print("Aguardando botão 'Ciente' aparecer...")
        botao_ciente = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and text()='Ciente']"))
        )
        botao_ciente.click()
        print("Botão 'Ciente' clicado com sucesso!")

        # Verifica se há erro após clicar no botão Ciente
        if verificar_e_reiniciar_se_erro(browser):
            print("Navegador foi fechado devido a erro. Saindo da função...")
            return False, None

        print("Navegando para menu de matrícula...")
        elemento = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='ThemeOfficeMainFolderText' and text()='Ensino']"))
        )
        elemento.click()
        
        elemento = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//td[@class='ThemeOfficeMenuFolderText' and contains(text(), 'Matrícula On-Line')]"))
        )
        elemento.click()

        elemento = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//td[@class='ThemeOfficeMenuItemText' and contains(text(), 'Realizar Matrícula Extraordinária')]"))
        )
        elemento.click()

        # Verifica se há erro após navegar para a página de matrícula
        if verificar_e_reiniciar_se_erro(browser):
            print("Navegador foi fechado devido a erro. Saindo da função...")
            return False, None

        print("Preenchendo nome da matéria...")
        botao_nome_materia = WebDriverWait(browser, TIME_TO_WAIT).until(EC.element_to_be_clickable((By.ID, 'form:txtNome')))
        botao_nome_materia.click()

        search_input_nome_materia = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located(
                (By.ID, 'form:txtNome')
            )
        )

        search_input_nome_materia.send_keys('ALGEBRA 1')
        search_input_nome_materia.send_keys(Keys.ENTER)

        # Verifica se há erro após preencher o nome da matéria
        if verificar_e_reiniciar_se_erro(browser):
            print("Navegador foi fechado devido a erro. Saindo da função...")
            return False, None

        
        search_input_horario_materia = WebDriverWait(browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located(
                (By.ID, 'form:txtHorario')
            )
        )    
        search_input_horario_materia.send_keys('36M12')

        search_input_horario_materia.send_keys(Keys.ENTER)
        
        
        print("Aguardando botão 'Selecionar Turma' ficar disponível...")
        # Aguarda o botão ficar disponível com refresh automático
        if not aguardar_botao_com_refresh(browser):
            print("Função aguardar_botao_com_refresh retornou False. Saindo da função...")
            return False, None

        try:
            # Localiza o campo de entrada pelo ID
            campo_data = WebDriverWait(browser, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:Data"))
            )

            # Clica no campo para focar nele
            campo_data.click()

            # Digita a data no campo
            campo_data.send_keys(DATA_NASCIMENTO)  # Substitua pela data de nascimento desejada
            print("Data inserida com sucesso!")

            campo_senha = WebDriverWait(browser, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:senha"))
            )
            campo_senha.click()
            campo_senha.send_keys(SENHA) #Substitua pela sua senha

            campo_confirma = WebDriverWait(browser, TIME_TO_WAIT).until(
                EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:btnConfirmar"))
            )
            campo_confirma.click()

            alert = Alert(browser)

            # Obtém o texto do pop-up
            print("Texto do pop-up:", alert.text)

            # Clica no botão "OK" (ou "Confirmar")
            alert.accept()
            print("Pop-up confirmado com sucesso!")

        except Exception as e:
            print(f"Primeira tentativa falhou: {e}")
            
            try:
                campo_cpf = WebDriverWait(browser, TIME_TO_WAIT).until(
                    EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:cpf"))
                )

                # Clica no campo para focar nele
                campo_cpf.click()

                # Digita o CPF no campo
                campo_cpf.send_keys(CPF)  # Substitua pelo CPF desejado
                print("CPF inserido com sucesso!")

                campo_senha = WebDriverWait(browser, TIME_TO_WAIT).until(
                    EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:senha"))
                )
                campo_senha.click()
                campo_senha.send_keys(SENHA) #Substitua pela sua senha
                print('senha inserida com sucesso!')
                campo_confirma = WebDriverWait(browser, TIME_TO_WAIT).until(
                    EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:btnConfirmar"))
                )
                campo_confirma.click()

                alert = Alert(browser)

                # Obtém o texto do pop-up
                print("Texto do pop-up:", alert.text)

                # Clica no botão "OK" (ou "Confirmar")
                alert.accept()
                print("Pop-up confirmado com sucesso!")

            except Exception as e2:
                print(f"Segunda tentativa falhou: {e2}")
                
                try:
                    campo_cpf.send_keys(CPF)  # Substitua pelo CPF desejado
                    print("CPF inserido com sucesso!")
                    campo_confirma = WebDriverWait(browser, TIME_TO_WAIT).until(
                        EC.element_to_be_clickable((By.ID, "j_id_jsp_334536566_1:btnConfirmar"))
                    )
                    campo_confirma.click()
                    WebDriverWait(browser, TIME_TO_WAIT).until(EC.alert_is_present())

                    # Muda o foco para o pop-up
                    alert = Alert(browser)

                    # Obtém o texto do pop-up
                    print("Texto do pop-up:", alert.text)

                    # Clica no botão "OK" (ou "Confirmar")
                    alert.accept()
                    print("Pop-up confirmado com sucesso!")
                    
                except Exception as e3:
                    print(f"Terceira tentativa falhou: {e3}")
                    raise Exception(f"Todas as tentativas de preenchimento falharam: {e3}")

        print("Processo de matrícula concluído com sucesso!")
        return True, browser

    except Exception as e:
        print(f"Erro durante a execução: {e}")
        
        # Verifica se o elemento 'sair-sistema' está presente
        if browser:
            try:
                elemento = browser.find_element(By.CLASS_NAME, 'sair-sistema')
                elemento.click()
                print("Elemento 'sair-sistema' encontrado e clicado.")
            except:
                print("Elemento 'sair-sistema' não encontrado.")
        
        # Retorna False e o browser para que possa ser fechado no loop principal
        return False, browser

if __name__ == '__main__':
    print("Script iniciado! Para parar, pressione Ctrl+C no terminal.")
    print("O script continuará tentando infinitamente até conseguir a matrícula OU ser interrompido manualmente.")
    print("Detecção automática de erros ativada - navegador será reiniciado quando necessário.")
    
    while True:
        browser = None
        try:
            print(f"\n{'='*50}")
            print("Iniciando nova tentativa de matrícula...")
            print(f"{'='*50}")
            
            # Chama main() e captura o browser retornado
            success, current_browser = main()
            browser = current_browser  # Atualiza a variável browser
            
            if success:
                print("Processo concluído com sucesso!")
                print("Matrícula realizada! Encerrando o script.")
                if browser:
                    try:
                        browser.quit()
                        print("Navegador fechado com sucesso.")
                    except Exception as e:
                        print(f"Erro ao fechar navegador: {e}")
                break  # Para o loop após sucesso
            else:
                # Se main() retornou False, significa que houve erro mas o browser foi fechado
                if current_browser is None:
                    print("Processo falhou e navegador foi fechado. Tentando novamente...")
                    continue
                else:
                    print("Processo falhou mas navegador ainda está aberto. Fechando...")
                    if browser:
                        try:
                            browser.quit()
                            print("Navegador fechado com sucesso.")
                        except Exception as e:
                            print(f"Erro ao fechar navegador: {e}")
                    continue
                
        except KeyboardInterrupt:
            print("\n\nScript interrompido pelo usuário (Ctrl+C). Encerrando...")
            if browser:
                try:
                    browser.quit()
                    print("Navegador fechado com sucesso.")
                except Exception as e:
                    print(f"Erro ao fechar navegador: {e}")
            break
        except Exception as e:
            print(f"Erro detectado: {e}")
            
            # Garante que o navegador seja fechado ANTES de tentar novamente
            if browser:
                try:
                    print("Fechando navegador antigo...")
                    browser.quit()
                    print("Navegador antigo fechado com sucesso.")
                    # Aguarda um pouco para garantir que o processo seja finalizado
                    time.sleep(2)
                except Exception as close_error:
                    print(f"Erro ao fechar navegador: {close_error}")
                    # Força o fechamento se necessário
                    try:
                        browser.close()
                    except:
                        pass
            
            print(f"Aguardando 0.2 segundos antes de tentar novamente...")
            time.sleep(0.2)