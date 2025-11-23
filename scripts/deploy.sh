#!/bin/bash
# Deployment script for AI Doctor Chatbot

set -e

echo "🚀 AI Doctor Chatbot - Deployment Script"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with production settings"
    exit 1
fi

# Load environment
source .env

# Check required variables
required_vars=("OPENAI_API_KEY" "SECRET_KEY" "DATABASE_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "✓ Environment variables validated"
echo ""

# Ask for deployment type
echo "Select deployment type:"
echo "1. Docker Compose (local/development)"
echo "2. Production (systemd service)"
echo "3. AWS (EC2)"
read -p "Enter choice (1-3): " deploy_choice

case $deploy_choice in
    1)
        echo ""
        echo "Deploying with Docker Compose..."
        docker-compose down
        docker-compose build
        docker-compose up -d
        echo ""
        echo "✅ Deployment completed!"
        echo "Application running at: http://localhost:8000"
        echo "API Docs: http://localhost:8000/api/docs"
        ;;
    2)
        echo ""
        echo "Deploying as systemd service..."

        # Build backend
        cd backend
        source venv/bin/activate
        pip install -r requirements.txt

        # Copy systemd service
        sudo cp ../scripts/doctor-ai.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable doctor-ai
        sudo systemctl restart doctor-ai

        echo "✅ Service deployed and started"
        echo "Check status: sudo systemctl status doctor-ai"
        ;;
    3)
        echo ""
        echo "AWS EC2 Deployment..."

        # Check if AWS CLI is installed
        if ! command -v aws &> /dev/null; then
            echo "❌ AWS CLI not found. Please install it first."
            exit 1
        fi

        read -p "Enter EC2 instance IP: " ec2_ip
        read -p "Enter SSH key path: " ssh_key

        echo "Deploying to EC2 instance $ec2_ip..."

        # Create deployment package
        tar -czf deploy.tar.gz backend/ .env docker-compose.yml

        # Copy to EC2
        scp -i $ssh_key deploy.tar.gz ubuntu@$ec2_ip:~/

        # Deploy on EC2
        ssh -i $ssh_key ubuntu@$ec2_ip << 'EOF'
            tar -xzf deploy.tar.gz
            cd doctor_assistant-
            docker-compose down
            docker-compose up -d --build
            rm ~/deploy.tar.gz
EOF

        echo "✅ Deployed to EC2"
        echo "Access at: http://$ec2_ip:8000"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
