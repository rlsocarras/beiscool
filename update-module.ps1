# update-module.ps1 - Script para actualizar el módulo beiscool
$MODULE_NAME = "beiscool"
$DB_NAME = "odoo"  # Cambia esto por el nombre de tu base de datos
$ODOO_PATH = "D:\Instalaciones\Odoo18\server"
$PYTHON_PATH = "D:\Instalaciones\Odoo18\python\python.exe"
$ADDONS_PATH = "D:\Instalaciones\Odoo18\server\addons"

Write-Host "🔄 Actualizando modulo $MODULE_NAME..." -ForegroundColor Cyan

# Cambiar directorio y ejecutar actualización
Set-Location $ODOO_PATH

# Actualizar el módulo
$process = Start-Process -FilePath $PYTHON_PATH `
    -ArgumentList "odoo-bin", "-u", $MODULE_NAME, "-d", $DB_NAME, "--addons-path=`"$ADDONS_PATH`"", "--stop-after-init" `
    -NoNewWindow -Wait -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host "✅ Modulo actualizado correctamente" -ForegroundColor Green
    
    $restart = Read-Host "¿Deseas reiniciar el servidor Odoo? (s/n)"
    if ($restart -eq 's') {
        Write-Host "🔄 Reiniciando servicio Odoo..." -ForegroundColor Yellow
        Restart-Service -Name "odoo-server-18.0" -Force -ErrorAction SilentlyContinue
        if ($?) {
            Write-Host "✅ Servicio Odoo reiniciado" -ForegroundColor Green
        } else {
            Write-Host "⚠️  No se pudo reiniciar el servicio. Intenta desde Administrador de tareas." -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "❌ Error al actualizar el módulo" -ForegroundColor Red
    Write-Host "Código de error: $($process.ExitCode)" -ForegroundColor Red
}

Read-Host "Presiona Enter para salir"
