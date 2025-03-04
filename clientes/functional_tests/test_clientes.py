# "C:\Users\paulo\OneDrive\_UNIVESP\programas\rewards\msedgedriver.exe"
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from django.contrib.auth.models import User
from django.urls import reverse

from clientes.models import Cliente

class TestClientes(StaticLiveServerTestCase):
    def setUp(self):
        # Instancie um objeto EdgeOption
        self.edge_options = webdriver.EdgeOptions()

        # Defina o modo sem cabeçalho
        self.edge_options.headless = True
        
        # Inicie o driver, passando edge_options
        self.driver = webdriver.Edge(options=self.edge_options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        User.objects.create_user(username='testuser', password='secretkey')

        # Login
        self.login_url = self.live_server_url + reverse('login')
        self.page = self.driver.get(self.login_url)
        usuario = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[2]/form/div[1]/input")
        usuario.send_keys('testuser')
        senha = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[2]/form/div[2]/input")
        senha.send_keys('secretkey')
        botao = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[2]/form/button")
        botao.click()

        self.driver.implicitly_wait(10)
        Cliente.objects.create(
            cpf="12345678901",
            nome="Fulano de Tal",
            data_nascimento="1981-01-21",
            telefone="18991234567",
            observacao_telefone="Recado com Júlio (vizinho)",
            telefone_whatsapp="18991234567",
            email="pauloadilson@gmail.com",
        )

        self.cliente1 = {
            "cpf":"12345678902",
            "nome":"Fulano de Tal",
            "data_nascimento":"21/01/1981",
            "telefone":"18991234567",
            "observacao_telefone":"Recado com Júlio (vizinho)",
            "telefone_whatsapp":"18991234567",
            "email":"pauloadilson@gmail.com",
        }

        self.clientes_url = self.live_server_url + reverse('clientes')
        self.adicionar_cliente_url = self.live_server_url + reverse('adicionar_cliente')
        self.cliente1_url = self.live_server_url + reverse('cliente', kwargs={'cpf': self.cliente1['cpf']})


    def tearDown(self):
        self.driver.quit()
    
    
    def test_clientes_page(self):
        # incluindo um cliente
        # testar se a página de clientes está funcionando
        self.page = self.driver.get(self.clientes_url)
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[1]/div")
        self.assertEqual(element.text, "Clientes")
        
        # verificar se o botão editar está presente
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[2]/table/tbody/tr[1]/td[7]/a[1]")
        name_attribute = element.get_attribute("atitle")
        self.assertEqual(name_attribute, "Editar")

        # verificar se o botão excluir está presente
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[2]/table/tbody/tr[1]/td[7]/a[2]")
        name_attribute = element.get_attribute("atitle")
        self.assertEqual(name_attribute, "Excluir")

        # verificar se o botão novo cliente está presente e funcionando
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[1]/p/a")
        self.assertEqual(element.text, "Novo Cliente")
        element.click()
        self.assertEqual(self.driver.current_url, self.adicionar_cliente_url)



    def test_adicionar_cliente_page(self):
        # testar se a página de novo cliente está funcionando
        self.page = self.driver.get(self.clientes_url)
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[1]/p/a")
        element.click()

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[1]/div")
        self.assertEqual(element.text, "Novo Cliente")
        
        # verificar se o botão salvar está presente
        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[8]/div/input[1]")
        name_attribute = element.get_attribute("value")
        self.assertEqual(name_attribute, "Salvar")
        
        # verificar se o botão voltar está presente e funcionando
        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[8]/div/input[2]")
        name_attribute = element.get_attribute("value")
        self.assertEqual(name_attribute, "Voltar")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.driver.execute_script("arguments[0].click();", element)
        self.assertEqual(self.driver.current_url, self.clientes_url)

        
    def test_adicionar_cliente_insert_and_check(self):
        # verificar se o formulário está funcionando
        self.page = self.driver.get(self.adicionar_cliente_url)
        self.driver.maximize_window()

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[1]/input")
        element.send_keys(self.cliente1['cpf'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[2]/input")
        element.send_keys(self.cliente1['nome'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[3]/input")
        element.send_keys(self.cliente1['data_nascimento'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[4]/input")
        element.send_keys(self.cliente1['telefone_whatsapp'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[5]/input")
        element.send_keys(self.cliente1['telefone'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[6]/textarea")
        element.send_keys(self.cliente1['observacao_telefone'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[7]/input")
        element.send_keys(self.cliente1['email'])

        element = self.driver.find_element(By.XPATH,"/html/body/div[2]/main/div/div[2]/form/div[8]/div/input[1]")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.driver.execute_script("arguments[0].click();", element)
        
        self.assertEqual(self.driver.current_url, self.cliente1_url)
        time.sleep(5)
        print('Esperando 5 segundos para verificar se o cliente foi salvo')
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div/div[1]/div")
        self.assertEqual(element.text, "Cliente")

        # verificar se o cliente foi salvo
        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[1]")
        self.assertEqual(element.text, self.cliente1['cpf'])

        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[2]")
        self.assertEqual(element.text, self.cliente1['nome'])

        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[3]")
        self.assertEqual(element.text, self.cliente1['data_nascimento'])

        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[4]")
        self.assertEqual(element.text, self.cliente1['telefone_whatsapp'])

        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[5]")
        self.assertEqual(element.text, self.cliente1['telefone'])

        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[6]")
        self.assertEqual(element.text, self.cliente1['observacao_telefone'])

        element = self.driver.find_element(By.XPATH,"/html/body/div/main/div[1]/div/dl/dd[7]")
        self.assertEqual(element.text, self.cliente1['email'])
