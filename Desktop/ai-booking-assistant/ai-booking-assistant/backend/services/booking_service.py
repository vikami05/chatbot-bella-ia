from datetime import datetime, timedelta, time
from models.booking import Booking
from database import db
from config.settings import Config
from integrations.n8n_webhook import send_booking_notification

class BookingService:
    """Servicio para gestionar reservas"""
    
    def create_booking(self, data: dict) -> dict:
        """Crear una nueva reserva"""
        try:
            # Validar datos requeridos
            required_fields = ['client_name', 'service', 'date', 'time']
            for field in required_fields:
                if field not in data or not data[field]:
                    return {
                        'success': False,
                        'message': f'Falta información: {field}'
                    }
            
            # Parsear fecha y hora
            booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            booking_time = datetime.strptime(data['time'], '%H:%M').time()
            
            # Validar servicio
            service = data['service'].lower()
            if service not in Config.SERVICES:
                return {
                    'success': False,
                    'message': f'Servicio no válido: {service}'
                }
            
            # Verificar disponibilidad
            if not self._is_available(booking_date, booking_time, Config.SERVICES[service]['duration']):
                return {
                    'success': False,
                    'message': 'Ese horario no está disponible. ¿Te puedo ofrecer otro?'
                }
            
            # Crear reserva
            booking = Booking(
                client_name=data['client_name'],
                client_phone=data.get('client_phone'),
                client_email=data.get('client_email'),
                service=service,
                booking_date=booking_date,
                booking_time=booking_time,
                duration=Config.SERVICES[service]['duration'],
                status='confirmed',
                notes=data.get('notes')
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Enviar notificación a n8n
            send_booking_notification(booking.to_dict())
            
            return {
                'success': True,
                'message': f'¡Perfecto! Tu turno está confirmado para {data["date"]} a las {data["time"]}.',
                'booking_id': booking.id
            }
        
        except Exception as e:
            db.session.rollback()
            print(f"Error creando reserva: {str(e)}")
            return {
                'success': False,
                'message': 'Hubo un error creando la reserva. Intentá de nuevo.'
            }
    
    def _is_available(self, date, time, duration) -> bool:
        """Verificar si un horario está disponible"""
        # Obtener reservas existentes para esa fecha
        existing_bookings = Booking.query.filter_by(
            booking_date=date,
            status='confirmed'
        ).all()
        
        # Convertir time a datetime para cálculos
        proposed_start = datetime.combine(date, time)
        proposed_end = proposed_start + timedelta(minutes=duration)
        
        for booking in existing_bookings:
            booking_start = datetime.combine(date, booking.booking_time)
            booking_end = booking_start + timedelta(minutes=booking.duration)
            
            # Verificar solapamiento
            if (proposed_start < booking_end and proposed_end > booking_start):
                return False
        
        return True
    
    def check_availability(self, data: dict) -> dict:
        """Verificar horarios disponibles para una fecha"""
        try:
            date_str = data.get('date')
            if not date_str:
                return {'slots': []}
            
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Generar slots cada 30 minutos
            slots = []
            start_time = datetime.strptime(Config.BUSINESS_HOURS['start'], '%H:%M').time()
            end_time = datetime.strptime(Config.BUSINESS_HOURS['end'], '%H:%M').time()
            
            current = datetime.combine(date, start_time)
            end = datetime.combine(date, end_time)
            
            while current < end:
                if self._is_available(date, current.time(), 30):
                    slots.append(current.strftime('%H:%M'))
                current += timedelta(minutes=30)
            
            return {
                'date': date_str,
                'slots': slots
            }
        
        except Exception as e:
            print(f"Error verificando disponibilidad: {str(e)}")
            return {'slots': []}
    
    def cancel_booking(self, data: dict) -> dict:
        """Cancelar una reserva"""
        try:
            booking_id = data.get('booking_id')
            client_name = data.get('client_name')
            
            query = Booking.query.filter_by(status='confirmed')
            
            if booking_id:
                booking = query.filter_by(id=booking_id).first()
            elif client_name:
                booking = query.filter_by(client_name=client_name).order_by(Booking.booking_date.desc()).first()
            else:
                return {
                    'success': False,
                    'message': 'Necesito tu nombre o el número de reserva para cancelar'
                }
            
            if not booking:
                return {
                    'success': False,
                    'message': 'No encontré tu reserva. ¿Verificaste el nombre?'
                }
            
            booking.status = 'cancelled'
            booking.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Tu turno del {booking.booking_date} a las {booking.booking_time.strftime("%H:%M")} fue cancelado.'
            }
        
        except Exception as e:
            db.session.rollback()
            print(f"Error cancelando reserva: {str(e)}")
            return {
                'success': False,
                'message': 'Hubo un error cancelando la reserva.'
            }
    
    def get_bookings(self, date_str: str = None) -> list:
        """Obtener lista de reservas"""
        query = Booking.query.filter_by(status='confirmed')
        
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(booking_date=date)
        
        return query.order_by(Booking.booking_date, Booking.booking_time).all()
