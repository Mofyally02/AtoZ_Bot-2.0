param(
    [string]$Python = "python"
)

Write-Host "Creating venv in .venv..."
$venvPath = ".venv"
& $Python -m venv $venvPath

Write-Host "Activating venv..."
& "$venvPath\Scripts\Activate.ps1"

Write-Host "Installing requirements..."
pip install -r requirements.txt

Write-Host "Installing Playwright browsers..."
python -m playwright install chromium

Write-Host "Done. Create a .env from env.example and fill credentials."


