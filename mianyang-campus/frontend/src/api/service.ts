import request from '@/utils/request'
import type { ServiceTicket } from '@/types'

export function getTickets(params?: { status?: string }) {
  return request.get<ServiceTicket[]>('/service/tickets', { params })
}

export function createTicket(data: { type: string; title: string; content: string }) {
  return request.post<ServiceTicket>('/service/tickets', data)
}

export function approveTicket(id: number, action: string) {
  return request.put(`/service/tickets/${id}/approve`, { action })
}
