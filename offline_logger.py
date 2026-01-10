"""
Network Offline Logger
Registra eventi di disconnessione rete in file JSON
"""
import json
import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OfflineLogger:
    """Logger per eventi offline della rete"""
    
    def __init__(self, log_file='logs/offline_events.json'):
        self.log_file = log_file
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Assicura che il file di log esista"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not log_path.exists():
            # Inizializza file con array vuoto
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def log_event(self, event_type, timestamp, duration_seconds=None, 
                  user_agent=None, page=None, additional_info=None):
        """
        Registra un evento offline
        
        Args:
            event_type: 'start' o 'end'
            timestamp: Timestamp ISO dell'evento
            duration_seconds: Durata offline (solo per 'end')
            user_agent: User agent del browser
            page: Pagina dove è avvenuto l'evento
            additional_info: Dict con info aggiuntive
        """
        try:
            # Leggi eventi esistenti
            with open(self.log_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # Crea nuovo evento
            event = {
                'event_type': event_type,
                'timestamp': timestamp,
                'local_timestamp': datetime.now().isoformat(),
                'duration_seconds': duration_seconds,
                'user_agent': user_agent,
                'page': page
            }
            
            if additional_info:
                event['additional_info'] = additional_info
            
            # Aggiungi evento
            events.append(event)
            
            # Mantieni solo ultimi 1000 eventi (pulizia automatica)
            if len(events) > 1000:
                events = events[-1000:]
            
            # Salva
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Evento offline registrato: {event_type} @ {timestamp}")
            
            # Log anche su file di log standard
            if event_type == 'start':
                logger.warning(f"Connessione persa: {timestamp}")
            else:
                logger.info(f"Connessione ripristinata: {timestamp}, durata: {duration_seconds}s")
            
        except Exception as e:
            logger.error(f"Errore log evento offline: {e}")
    
    def get_events(self, limit=None, event_type=None):
        """
        Recupera eventi dal log
        
        Args:
            limit: Numero massimo eventi da restituire
            event_type: Filtra per tipo ('start' o 'end')
        
        Returns:
            List di eventi
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # Filtra per tipo se richiesto
            if event_type:
                events = [e for e in events if e.get('event_type') == event_type]
            
            # Limita numero risultati
            if limit:
                events = events[-limit:]
            
            return events
            
        except Exception as e:
            logger.error(f"Errore lettura eventi offline: {e}")
            return []
    
    def get_statistics(self, hours=24):
        """
        Calcola statistiche eventi offline
        
        Args:
            hours: Ore da analizzare (default 24)
        
        Returns:
            Dict con statistiche
        """
        try:
            from datetime import timedelta
            
            events = self.get_events()
            now = datetime.now()
            cutoff = now - timedelta(hours=hours)
            
            # Filtra eventi nel periodo
            recent_events = []
            for event in events:
                try:
                    event_time = datetime.fromisoformat(event['local_timestamp'])
                    if event_time >= cutoff:
                        recent_events.append(event)
                except:
                    continue
            
            # Conta eventi
            start_events = [e for e in recent_events if e['event_type'] == 'start']
            end_events = [e for e in recent_events if e['event_type'] == 'end']
            
            # Calcola durata totale offline
            total_offline_seconds = sum(
                e.get('duration_seconds', 0) or 0 
                for e in end_events
            )
            
            # Durata media
            avg_duration = (
                total_offline_seconds / len(end_events) 
                if end_events else 0
            )
            
            return {
                'period_hours': hours,
                'total_disconnections': len(start_events),
                'total_offline_seconds': total_offline_seconds,
                'total_offline_minutes': round(total_offline_seconds / 60, 2),
                'average_duration_seconds': round(avg_duration, 2),
                'last_event': recent_events[-1] if recent_events else None
            }
            
        except Exception as e:
            logger.error(f"Errore calcolo statistiche: {e}")
            return {}


# Singleton globale
_offline_logger = None

def get_offline_logger():
    """Ottiene istanza singleton dell'offline logger"""
    global _offline_logger
    if _offline_logger is None:
        _offline_logger = OfflineLogger()
    return _offline_logger
