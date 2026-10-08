import { describe, it, expect } from 'vitest';
import {
  NotificationItem,
  NotificationListResponse,
  NotificationScanResult,
} from '@/types/notification';
import { formatRelativeTime, getTypeBadgeDetails } from './notification_utils';

describe('Module 10: Notification & Alert System Frontend Models and Helpers', () => {
  it('validates NotificationItem data contracts and fields', () => {
    const item: NotificationItem = {
      id: 42,
      user_id: 1,
      type: 'FUNDING',
      title: 'NSF AI Exploration Grant',
      message: 'New research opportunity closing soon.',
      related_module: 'funding',
      related_record_id: 'fnd_101',
      target_url: '/funding',
      priority: 'HIGH',
      is_read: false,
      created_at: new Date().toISOString(),
    };

    expect(item.id).toBe(42);
    expect(item.type).toBe('FUNDING');
    expect(item.priority).toBe('HIGH');
    expect(item.target_url).toBe('/funding');
    expect(item.is_read).toBe(false);
  });

  it('validates NotificationListResponse structure', () => {
    const resp: NotificationListResponse = {
      items: [
        {
          id: 1,
          user_id: 1,
          type: 'PATENT',
          title: 'Quantum Processor Patent Published',
          message: 'Patent filed by IBM Quantum.',
          related_module: 'patents',
          related_record_id: 'pat_202',
          target_url: '/patents',
          priority: 'MEDIUM',
          is_read: true,
          created_at: new Date().toISOString(),
        },
      ],
      total: 1,
      unread_count: 0,
    };

    expect(resp.total).toBe(1);
    expect(resp.unread_count).toBe(0);
    expect(resp.items[0].type).toBe('PATENT');
  });

  it('validates NotificationScanResult model', () => {
    const scan: NotificationScanResult = {
      scanned_modules: ['funding', 'patents', 'technology', 'research', 'commercialization', 'platform'],
      generated_count: 3,
      notifications: [
        {
          id: 10,
          user_id: 1,
          type: 'TECHNOLOGY',
          title: 'Emerging Technology Signal',
          message: 'Increased growth signal in AI.',
          related_module: 'technology_intelligence',
          related_record_id: 'tech_ai',
          target_url: '/technology-intelligence',
          priority: 'HIGH',
          is_read: false,
          created_at: new Date().toISOString(),
        },
      ],
    };

    expect(scan.generated_count).toBe(3);
    expect(scan.scanned_modules).toContain('funding');
    expect(scan.scanned_modules).toContain('commercialization');
  });

  it('formats relative timestamps accurately', () => {
    const now = new Date();
    const tenSecondsAgo = new Date(now.getTime() - 10 * 1000).toISOString();
    const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000).toISOString();
    const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString();
    const threeDaysAgo = new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString();

    expect(formatRelativeTime(tenSecondsAgo)).toBe('Just now');
    expect(formatRelativeTime(fiveMinutesAgo)).toBe('5m ago');
    expect(formatRelativeTime(twoHoursAgo)).toBe('2h ago');
    expect(formatRelativeTime(threeDaysAgo)).toBe('3d ago');
  });

  it('returns distinct badge details across all 6 notification types', () => {
    const fundingBadge = getTypeBadgeDetails('FUNDING');
    const patentBadge = getTypeBadgeDetails('PATENT');
    const techBadge = getTypeBadgeDetails('TECHNOLOGY');
    const trendBadge = getTypeBadgeDetails('RESEARCH_TREND');
    const commBadge = getTypeBadgeDetails('COMMERCIALIZATION');
    const platBadge = getTypeBadgeDetails('PLATFORM');

    expect(fundingBadge.label).toBe('Funding Radar');
    expect(patentBadge.label).toBe('Patent IP');
    expect(techBadge.label).toBe('Tech Intelligence');
    expect(trendBadge.label).toBe('Research Trend');
    expect(commBadge.label).toBe('Commercialization');
    expect(platBadge.label).toBe('Platform Alert');

    expect(fundingBadge.text).toContain('emerald');
    expect(patentBadge.text).toContain('violet');
    expect(techBadge.text).toContain('cyan');
    expect(trendBadge.text).toContain('blue');
    expect(commBadge.text).toContain('amber');
  });

  it('correctly filters notifications by category', () => {
    const notifications: NotificationItem[] = [
      {
        id: 1,
        user_id: 1,
        type: 'FUNDING',
        title: 'Grant Opportunity',
        message: 'Grant',
        priority: 'HIGH',
        is_read: false,
        created_at: new Date().toISOString(),
      },
      {
        id: 2,
        user_id: 1,
        type: 'PATENT',
        title: 'Patent Alert',
        message: 'Patent',
        priority: 'MEDIUM',
        is_read: false,
        created_at: new Date().toISOString(),
      },
    ];

    const fundingOnly = notifications.filter((n) => n.type === 'FUNDING');
    const patentOnly = notifications.filter((n) => n.type === 'PATENT');
    const unread = notifications.filter((n) => !n.is_read);

    expect(fundingOnly.length).toBe(1);
    expect(patentOnly.length).toBe(1);
    expect(unread.length).toBe(2);
  });
});
