import { infoSections, InfoRule } from './infoData';

export function findInfoRuleById(ruleId: string): InfoRule | null {
  for (const section of infoSections) {
    const found = section.rules.find((r) => r.id === ruleId);
    if (found) return found;
  }
  return null;
}

export function getHintLines(ruleIds: string[]): Array<{ id: string; title: string; summary: string }> {
  const seen = new Set<string>();
  const out: Array<{ id: string; title: string; summary: string }> = [];

  for (const id of ruleIds) {
    if (!id || seen.has(id)) continue;
    seen.add(id);

    const rule = findInfoRuleById(id);
    if (rule) {
      out.push({ id, title: rule.title, summary: rule.summary });
    } else {
      // Fallback if backend sends an unknown id
      out.push({ id, title: id, summary: '' });
    }
  }

  return out;
}