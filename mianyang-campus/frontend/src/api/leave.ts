import request from '@/utils/request'
import type { LeaveRequestOut, LeaveRequestCreate } from '@/types'

export function getMyLeaves() {
  return request.get<LeaveRequestOut[]>('/leave/my')
}

export function createLeave(data: LeaveRequestCreate) {
  return request.post<LeaveRequestOut>('/leave/create', data)
}

export function deleteLeave(id: number) {
  return request.delete(`/leave/${id}`)
}

export function getPendingLeaves() {
  return request.get<LeaveRequestOut[]>('/leave/pending')
}

export function reviewLeave(id: number, action: 'approve' | 'reject', reject_reason?: string) {
  return request.post(`/leave/${id}/review`, { action, reject_reason })
}
