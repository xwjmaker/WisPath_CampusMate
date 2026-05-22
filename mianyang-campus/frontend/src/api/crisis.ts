import request from '@/utils/request'
import type { CrisisAlert } from '@/types'

export function getAlerts(resolved?: boolean) {
  const params = resolved !== undefined ? { resolved } : {}
  return request.get<CrisisAlert[]>('/crisis/alerts', { params })
}

export function getStudentAlerts(studentId: number) {
  return request.get<CrisisAlert[]>(`/crisis/students/${studentId}/alerts`)
}

export function resolveAlert(id: number, resolved = true) {
  return request.post(`/crisis/${id}/resolve`, { resolved })
}
