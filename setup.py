"""
Script de configuração inicial para AWS SWF.

Este script registra o domínio, tipo de workflow e todas as atividades
necessárias para executar a aplicação.

Execute este script antes de iniciar os workers.
"""

from swf_client import SWFClient
from activity_worker import ActivityWorker
from config import Config

def setup():
    """
    Configura todos os recursos necessários no AWS SWF.
    
    Registra:
    1. Domínio SWF
    2. Tipo de workflow
    3. Todos os tipos de atividades
    """
    print("=" * 60)
    print("AWS SWF Setup - Configuração Inicial")
    print("=" * 60)
    print()
    
    # Inicializa cliente SWF
    print("1. Inicializando cliente SWF...")
    swf_client = SWFClient()
    print(f"   Região: {Config.AWS_REGION}")
    print(f"   Domínio: {Config.SWF_DOMAIN}")
    print()
    
    # Registra domínio
    print("2. Registrando domínio SWF...")
    swf_client.register_domain()
    print()
    
    # Registra tipo de workflow
    print("3. Registrando tipo de workflow...")
    swf_client.register_workflow_type()
    print()
    
    # Registra atividades
    print("4. Registrando atividades...")
    activity_worker = ActivityWorker()
    activity_worker.register_activities()
    print()
    
    print("=" * 60)
    print("✓ Setup concluído com sucesso!")
    print("=" * 60)
    print()
    print("Próximos passos:")
    print("1. Abra um terminal e execute: python decision_worker.py")
    print("2. Abra outro terminal e execute: python activity_worker.py")
    print("3. Abra um terceiro terminal e execute: python workflow_starter.py")
    print()

if __name__ == '__main__':
    try:
        setup()
    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        print("\nVerifique:")
        print("- Credenciais AWS no arquivo .env")
        print("- Permissões IAM para SWF")
        print("- Conectividade com AWS")
