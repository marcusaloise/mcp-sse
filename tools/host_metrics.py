import requests
import time
import logging
from typing import Dict, Optional, Union

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeExporterClient:
    """Cliente para coletar métricas do Node Exporter."""
    
    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.timeout = timeout
    
    def _fetch_metrics(self) -> str:
        """Faz requisição para buscar métricas."""
        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar métricas: {e}")
            raise
    
    def _parse_metric_value(self, data: str, metric_name: str, 
                          filters: Dict[str, str] = None) -> Optional[float]:
        """
        Extrai valor de uma métrica específica com filtros opcionais.
        
        Args:
            data: Dados de métricas em formato texto
            metric_name: Nome da métrica
            filters: Dicionário com filtros (ex: {'cpu': '0', 'mode': 'user'})
        
        Returns:
            Valor da métrica ou None se não encontrada
        """
        filters = filters or {}
        
        for line in data.split('\n'):
            if line.startswith(metric_name):
                # Verifica se todos os filtros estão presentes na linha
                if all(f'{k}="{v}"' in line for k, v in filters.items()):
                    try:
                        return float(line.split()[1])
                    except (IndexError, ValueError) as e:
                        logger.warning(f"Erro ao parsear linha: {line}. Erro: {e}")
                        continue
        return None
    
    def get_cpu_usage(self, cpu: str = "0", interval: float = 1.0) -> float:
        """
        Calcula o percentual de uso de CPU.
        
        Args:
            cpu: ID da CPU (padrão "0")
            interval: Intervalo entre medições em segundos
        
        Returns:
            Percentual de uso da CPU
        """
        try:
            # Primeira medição
            data_a = self._fetch_metrics()
            cpu_stats_a = self._get_cpu_stats(data_a, cpu)
            
            # Aguarda intervalo
            time.sleep(interval)
            
            # Segunda medição
            data_b = self._fetch_metrics()
            cpu_stats_b = self._get_cpu_stats(data_b, cpu)
            
            # Calcula diferenças
            total_diff = cpu_stats_b['total'] - cpu_stats_a['total']
            idle_diff = cpu_stats_b['idle'] - cpu_stats_a['idle']
            
            if total_diff > 0:
                cpu_percent = 100.0 * (1.0 - (idle_diff / total_diff))
                return round(cpu_percent, 2)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Erro ao calcular uso de CPU: {e}")
            return 0.0
    
    def _get_cpu_stats(self, data: str, cpu: str) -> Dict[str, float]:
        """Extrai estatísticas de CPU dos dados."""
        modes = ['user', 'system', 'idle', 'iowait', 'irq', 'softirq']
        stats = {}
        
        for mode in modes:
            value = self._parse_metric_value(
                data, 'node_cpu_seconds_total', 
                {'cpu': cpu, 'mode': mode}
            )
            stats[mode] = value or 0.0
        
        stats['total'] = sum(stats.values())
        return stats
    
    def get_memory_usage(self) -> Dict[str, Union[int, float]]:
        """
        Coleta informações de uso de memória.
        
        Returns:
            Dicionário com informações de memória
        """
        try:
            data = self._fetch_metrics()
            
            mem_total = self._parse_metric_value(data, 'node_memory_MemTotal_bytes')
            mem_available = self._parse_metric_value(data, 'node_memory_MemAvailable_bytes')
            
            if mem_total is None or mem_available is None:
                logger.warning("Métricas de memória não encontradas")
                return {}
            
            mem_total = int(mem_total)
            mem_available = int(mem_available)
            mem_used = mem_total - mem_available
            mem_percent = round((mem_used / mem_total) * 100, 2) if mem_total > 0 else 0
            
            return {
                'total_bytes': mem_total,
                'available_bytes': mem_available,
                'used_bytes': mem_used,
                'used_percent': mem_percent
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter uso de memória: {e}")
            return {}
    
    def get_disk_usage(self, mountpoint: str = "/") -> Dict[str, Union[int, float]]:
        """
        Coleta informações de uso de disco.
        
        Args:
            mountpoint: Ponto de montagem do disco
        
        Returns:
            Dicionário com informações de disco
        """
        try:
            data = self._fetch_metrics()
            
            filters = {'mountpoint': mountpoint}
            disk_total = self._parse_metric_value(data, 'node_filesystem_size_bytes', filters)
            disk_free = self._parse_metric_value(data, 'node_filesystem_free_bytes', filters)
            
            if disk_total is None or disk_free is None:
                logger.warning(f"Métricas de disco para {mountpoint} não encontradas")
                return {}
            
            disk_total = int(disk_total)
            disk_free = int(disk_free)
            disk_used = disk_total - disk_free
            disk_percent = round((disk_used / disk_total) * 100, 2) if disk_total > 0 else 0
            
            return {
                'total_bytes': disk_total,
                'free_bytes': disk_free,
                'used_bytes': disk_used,
                'used_percent': disk_percent
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter uso de disco: {e}")
            return {}
    
    def get_load_average(self) -> Dict[str, float]:
        """
        Coleta informações de load average.
        
        Returns:
            Dicionário com load averages
        """
        try:
            data = self._fetch_metrics()
            
            load_metrics = ['node_load1', 'node_load5', 'node_load15']
            load_data = {}
            
            for metric in load_metrics:
                value = self._parse_metric_value(data, metric)
                if value is not None:
                    period = metric.replace('node_load', '')
                    load_data[f'load_{period}min'] = round(value, 2)
            
            return load_data
            
        except Exception as e:
            logger.error(f"Erro ao obter load average: {e}")
            return {}
    
    def get_all_metrics(self, cpu: str = "0", mountpoint: str = "/") -> Dict:
        """
        Coleta todas as métricas em uma única chamada.
        
        Args:
            cpu: ID da CPU
            mountpoint: Ponto de montagem do disco
        
        Returns:
            Dicionário com todas as métricas
        """
        metrics = {}
        
        # CPU (requer duas medições)
        metrics['cpu'] = {'usage_percent': self.get_cpu_usage(cpu)}
        
        # Memória
        metrics['memory'] = self.get_memory_usage()
        
        # Disco
        metrics['disk'] = self.get_disk_usage(mountpoint)
        
        # Load Average
        metrics['load'] = self.get_load_average()
        
        return metrics
