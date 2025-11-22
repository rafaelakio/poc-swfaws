#!/bin/bash
# Script de automação para Linux/Mac
# Facilita a execução dos componentes da aplicação

show_menu() {
    echo ""
    echo "========================================"
    echo "  AWS SWF Workflow - Menu Principal"
    echo "========================================"
    echo ""
    echo "1. Setup inicial (registrar domínio e workflow)"
    echo "2. Iniciar Decision Worker"
    echo "3. Iniciar Activity Worker"
    echo "4. Executar demonstração"
    echo "5. Executar workflow customizado"
    echo "6. Sair"
    echo ""
}

setup() {
    echo ""
    echo "Executando setup inicial..."
    python setup.py
    read -p "Pressione Enter para continuar..."
}

decision_worker() {
    echo ""
    echo "Iniciando Decision Worker..."
    echo "Pressione Ctrl+C para parar"
    python decision_worker.py
}

activity_worker() {
    echo ""
    echo "Iniciando Activity Worker..."
    echo "Pressione Ctrl+C para parar"
    python activity_worker.py
}

demo() {
    echo ""
    echo "Executando demonstração..."
    echo ""
    echo "IMPORTANTE: Certifique-se de que os workers estão rodando!"
    echo "- Decision Worker (em outro terminal)"
    echo "- Activity Worker (em outro terminal)"
    echo ""
    read -p "Pressione Enter para continuar..."
    python demo.py
    read -p "Pressione Enter para continuar..."
}

custom_workflow() {
    echo ""
    echo "Executando workflow customizado..."
    python workflow_starter.py
    read -p "Pressione Enter para continuar..."
}

# Loop principal
while true; do
    show_menu
    read -p "Escolha uma opção (1-6): " choice
    
    case $choice in
        1) setup ;;
        2) decision_worker ;;
        3) activity_worker ;;
        4) demo ;;
        5) custom_workflow ;;
        6) echo ""; echo "Até logo!"; exit 0 ;;
        *) echo "Opção inválida!" ;;
    esac
done
