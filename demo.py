"""
Script de demonstração da aplicação AWS SWF.

Este script demonstra como usar a aplicação para processar
um pedido de e-commerce do início ao fim.

Execute este script após iniciar os workers:
1. python decision_worker.py (em um terminal)
2. python activity_worker.py (em outro terminal)
3. python demo.py (neste terminal)
"""

from workflow_starter import WorkflowStarter
import time
import json

def print_separator():
    """Imprime uma linha separadora."""
    print("\n" + "=" * 70 + "\n")

def demo_basic_workflow():
    """
    Demonstração 1: Workflow básico com sucesso.
    
    Inicia um workflow simples e monitora sua execução.
    """
    print_separator()
    print("DEMONSTRAÇÃO 1: Workflow Básico")
    print_separator()
    
    starter = WorkflowStarter()
    
    # Dados do pedido
    order_data = {
        'order_id': 'DEMO-001',
        'customer_id': 'CUST-12345',
        'items': [
            {'sku': 'PROD-001', 'name': 'Notebook', 'quantity': 1, 'price': 3500.00},
            {'sku': 'PROD-002', 'name': 'Mouse', 'quantity': 2, 'price': 50.00}
        ],
        'total': 3600.00,
        'payment_method': 'credit_card'
    }
    
    print("📦 Dados do Pedido:")
    print(json.dumps(order_data, indent=2, ensure_ascii=False))
    print()
    
    # Inicia o workflow
    print("🚀 Iniciando workflow...")
    result = starter.start_workflow(order_data)
    
    workflow_id = result['workflow_id']
    run_id = result['run_id']
    
    print(f"✓ Workflow iniciado com sucesso!")
    print(f"  Workflow ID: {workflow_id}")
    print(f"  Run ID: {run_id}")
    print()
    
    # Aguarda um pouco para o workflow processar
    print("⏳ Aguardando processamento (10 segundos)...")
    time.sleep(10)
    
    # Consulta histórico
    print("\n📊 Consultando histórico de eventos...")
    events = starter.get_workflow_history(workflow_id, run_id)
    
    print(f"\nTotal de eventos: {len(events)}")
    print("\nÚltimos 5 eventos:")
    for event in events[-5:]:
        event_type = event['eventType']
        timestamp = event['eventTimestamp']
        print(f"  [{timestamp}] {event_type}")
    
    print_separator()
    print("✓ Demonstração 1 concluída!")
    print_separator()
    
    return workflow_id, run_id

def demo_workflow_monitoring(workflow_id, run_id):
    """
    Demonstração 2: Monitoramento de workflow.
    
    Mostra como consultar o histórico detalhado de um workflow.
    """
    print_separator()
    print("DEMONSTRAÇÃO 2: Monitoramento de Workflow")
    print_separator()
    
    starter = WorkflowStarter()
    
    print(f"🔍 Analisando workflow: {workflow_id}")
    print()
    
    # Obtém histórico completo
    events = starter.get_workflow_history(workflow_id, run_id)
    
    # Analisa eventos
    activities_completed = []
    activities_failed = []
    
    for event in events:
        event_type = event['eventType']
        
        if event_type == 'ActivityTaskCompleted':
            attrs = event['activityTaskCompletedEventAttributes']
            # Busca o evento de agendamento
            scheduled_event = next(
                e for e in events 
                if e['eventId'] == attrs['scheduledEventId']
            )
            activity_name = scheduled_event['activityTaskScheduledEventAttributes']['activityType']['name']
            activities_completed.append(activity_name)
        
        elif event_type == 'ActivityTaskFailed':
            attrs = event['activityTaskFailedEventAttributes']
            scheduled_event = next(
                e for e in events 
                if e['eventId'] == attrs['scheduledEventId']
            )
            activity_name = scheduled_event['activityTaskScheduledEventAttributes']['activityType']['name']
            activities_failed.append(activity_name)
    
    print("📈 Estatísticas:")
    print(f"  Total de eventos: {len(events)}")
    print(f"  Atividades completadas: {len(activities_completed)}")
    print(f"  Atividades falhadas: {len(activities_failed)}")
    print()
    
    if activities_completed:
        print("✓ Atividades Completadas:")
        for activity in activities_completed:
            print(f"  - {activity}")
    
    if activities_failed:
        print("\n✗ Atividades Falhadas:")
        for activity in activities_failed:
            print(f"  - {activity}")
    
    print_separator()
    print("✓ Demonstração 2 concluída!")
    print_separator()

def main():
    """Função principal que executa todas as demonstrações."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                                                                ║")
    print("║          AWS SWF - Demonstração Interativa                    ║")
    print("║                                                                ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    try:
        # Demonstração 1: Workflow básico
        workflow_id, run_id = demo_basic_workflow()
        
        # Aguarda um pouco mais
        print("\n⏳ Aguardando mais 5 segundos para garantir conclusão...")
        time.sleep(5)
        
        # Demonstração 2: Monitoramento
        demo_workflow_monitoring(workflow_id, run_id)
        
        # Conclusão
        print("\n")
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                                                                ║")
        print("║                  Demonstração Concluída!                      ║")
        print("║                                                                ║")
        print("║  Próximos passos:                                             ║")
        print("║  1. Explore EXAMPLES.md para mais casos de uso               ║")
        print("║  2. Consulte FAQ.md para dúvidas comuns                      ║")
        print("║  3. Customize as atividades em activity_worker.py            ║")
        print("║                                                                ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print("\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante demonstração: {e}")
        print("\nVerifique se:")
        print("1. Os workers estão rodando (decision_worker.py e activity_worker.py)")
        print("2. As credenciais AWS estão configuradas no .env")
        print("3. O setup foi executado (python setup.py)")

if __name__ == '__main__':
    main()
