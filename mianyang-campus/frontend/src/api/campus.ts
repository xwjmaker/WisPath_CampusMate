import request from '@/utils/request'
import type { CampusFigure, CampusScenery, Announcement } from '@/types'

export function getFigures(category?: string) {
  return request.get<CampusFigure[]>('/campus/figures', { params: { category } })
}

export function getSceneries(area?: string) {
  return request.get<CampusScenery[]>('/campus/sceneries', { params: { area } })
}

export function getAnnouncements() {
  return request.get<Announcement[]>('/campus/announcements')
}

export function getGallery() {
  return request.get<GalleryImage[]>('/campus/gallery')
}

export interface GalleryImage {
  title: string
  image_url: string
  campus: string
}
