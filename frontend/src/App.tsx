import { useCallback, useEffect, useMemo, useState } from 'react'
import type { CSSProperties, FormEvent } from 'react'
import { Activity, BadgeCheck, Banknote, Check, ChevronRight, ClipboardList, Clock3, CreditCard, Heart, LoaderCircle, Package, RefreshCw, Send, Sparkles, Users, X } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? '' : `http://${window.location.hostname}:8000`)
type Ticket = { id: number; type: string; requester: string; subject: string; status: string; created_at: string }
type Event = { time?: string; agent_name?: string; action?: string; result?: { summary?: string; actions?: string[]; customer_response_draft?: string }; tool_calls?: { tool: string; args?: unknown; result?: string }[]; stop_reason?: string }
type Cash = { name: string; balance: number; date: string }
type Approval = { kind: string; ref_id: string; amount: string; account: string; approved_by: string; description: string }

const AGENTS: Record<string, { label: string; icon: string; accent: string; tint: string }> = {
  boss: { label: 'Boss', icon: '♕', accent: '#b95d87', tint: '#fbe4ee' },
  inventory: { label: 'Inventory', icon: '✿', accent: '#5c8e95', tint: '#e1f2f0' },
  accounting: { label: 'Accounting', icon: '₿', accent: '#b98942', tint: '#fff1d8' },
  facilities: { label: 'Facilities', icon: '⌂', accent: '#8471a8', tint: '#eee9fa' },
  customer_service: { label: 'Customer service', icon: '♡', accent: '#d47184', tint: '#ffe5e9' },
}
const NAV_ITEMS = [
  { key: 'tickets', icon: ClipboardList, label: 'Tickets' },
  { key: 'team', icon: Users, label: 'Agent team' },
  { key: 'approvals', icon: BadgeCheck, label: 'Approvals' },
  { key: 'cash', icon: Banknote, label: 'Cash' },
  { key: 'activity', icon: Activity, label: 'Agent activity' },
]

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { headers: { 'Content-Type': 'application/json' }, ...options })
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || `Request failed (${response.status})`)
  return response.json()
}

function Mascot({ mini = false }: { mini?: boolean }) {
  return <div className={`mascot ${mini ? 'mascot-mini' : ''}`} aria-label="pink bunny mascot" role="img">
    <span className="ear ear-left" /><span className="ear ear-right" /><span className="mascot-head"><i className="eye eye-left" /><i className="eye eye-right" /><b className="nose" /></span>
    <span className="mascot-body"><b className="bow bow-left" /><b className="bow bow-right" /><b className="bow-knot" /></span>
    {!mini && <><span className="gift gift-one" /><span className="gift gift-two" /><span className="pearl pearl-one" /><span className="pearl pearl-two" /><span className="coffee">☕</span></>}
  </div>
}

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [cash, setCash] = useState<Cash | null>(null)
  const [events, setEvents] = useState<Event[]>([])
  const [selected, setSelected] = useState<number | null>(null)
  const [view, setView] = useState('tickets')
  const [running, setRunning] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [approval, setApproval] = useState<Approval>({ kind: 'invoice', ref_id: '', amount: '', account: 'checking', approved_by: '', description: '' })

  const refresh = useCallback(async () => {
    try {
      const [ticketData, cashData, eventData] = await Promise.all([request<{ tickets: Ticket[] }>('/api/tickets'), request<Cash>('/api/cash'), request<{ events: Event[] }>('/api/events?limit=80')])
      setTickets(ticketData.tickets); setCash(cashData); setEvents(eventData.events); setError('')
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not reach the backend') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { refresh(); const timer = window.setInterval(refresh, 6000); return () => window.clearInterval(timer) }, [refresh])
  const openCount = tickets.filter(ticket => ticket.status.toLowerCase() === 'open').length
  const selectedTicket = tickets.find(ticket => ticket.id === selected)
  const recentEvents = useMemo(() => [...events].reverse(), [events])

  async function runSelected() {
    if (!selected) return
    setRunning(true); setNotice('')
    try { await request(`/api/tickets/${selected}/run`, { method: 'POST' }); setNotice(`Ticket ${selected} team run completed.`); await refresh(); setView('activity') }
    catch (e) { setError(e instanceof Error ? e.message : 'The team run failed') }
    finally { setRunning(false) }
  }

  async function approve(event: FormEvent) {
    event.preventDefault(); setNotice('');
    try { await request('/api/approvals', { method: 'POST', body: JSON.stringify({ ...approval, ref_id: approval.ref_id ? Number(approval.ref_id) : null, amount: Number(approval.amount) }) }); setNotice('Approved payment recorded and balance refreshed.'); setApproval({ ...approval, amount: '', approved_by: '' }); await refresh() }
    catch (e) { setError(e instanceof Error ? e.message : 'Approval failed') }
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="sidebar-brand"><div className="brand-bow"><span /><span /><b /></div><div><strong>Campus Customs</strong><small>agent atelier</small></div></div>
      <div className="sidebar-rule" />
      <nav className="side-nav" aria-label="Dashboard navigation">
        {NAV_ITEMS.map(({ key, icon: Icon, label }) => <button key={key} className={view === key ? 'nav-active' : ''} onClick={() => setView(key)}><Icon size={17} />{label}<ChevronRight size={14} /></button>)}
      </nav>
      <div className="sidebar-mascot"><Mascot /><p>soft paws,<br /><em>serious work.</em></p></div>
      <div className="sidebar-foot"><span className="pearl-dot" /> connected to MCP <span className="status-dot" /></div>
    </aside>
    <main className="main-content">
      <Mascot mini />
      <header className="topbar"><div><p className="eyebrow">Tuesday · agent atelier</p><h1>Good afternoon, <i>desk darling.</i></h1><p className="subhead">A polished view of every ticket, handoff, and approval.</p></div><button className="refresh-button" onClick={refresh}><RefreshCw size={15} /> Refresh</button></header>
      {error && <div className="alert error"><X size={16} /> {error}<button onClick={() => setError('')}>dismiss</button></div>}
      {notice && <div className="alert success"><Check size={16} /> {notice}</div>}
      <section className="summary-grid"><div className="summary-card blush"><span className="summary-icon"><ClipboardList size={18} /></span><small>Open tickets</small><strong>{loading ? '—' : openCount}</strong><em>live from the desk</em></div><div className="summary-card champagne"><span className="summary-icon"><CreditCard size={18} /></span><small>Checking balance</small><strong>{cash ? `$${cash.balance.toLocaleString()}` : '—'}</strong><em>{cash?.date || 'loading'} · no negative balances</em></div><div className="summary-card pearl-card"><span className="summary-icon"><Users size={18} /></span><small>Agent team</small><strong>5</strong><em>boss + four specialists</em></div></section>

      {(view === 'tickets' || view === 'team') && <section className="content-section"><div className="section-heading"><div><p className="eyebrow">the workroom</p><h2>Desk tickets</h2></div><span className="section-note"><span className="status-dot" /> live status</span></div><div className="ticket-layout"><div className="ticket-list">{loading ? <div className="empty-state"><div className="sleeping">⌒ᴥ⌒</div><p>Waking the desk…</p></div> : tickets.map(ticket => <button key={ticket.id} className={`ticket-card ${selected === ticket.id ? 'ticket-selected' : ''}`} onClick={() => setSelected(ticket.id)}><span className="ticket-number">#{ticket.id}</span><span className="ticket-info"><strong>{ticket.subject}</strong><small>{ticket.requester} · {ticket.type.replace('_', ' ')}</small></span><span className={`status-pill ${ticket.status.toLowerCase()}`}>{ticket.status}</span><ChevronRight size={16} /></button>)}{!loading && !tickets.length && <div className="empty-state"><div className="sleeping">z<span>z</span>z</div><p>No tickets are resting here.</p></div>}</div><div className="ticket-detail">{selectedTicket ? <><div className="detail-top"><div><span className="ticket-number">TICKET {selectedTicket.id}</span><h3>{selectedTicket.subject}</h3><p>{selectedTicket.requester} · created {selectedTicket.created_at}</p></div><span className={`status-pill ${selectedTicket.status.toLowerCase()}`}>{selectedTicket.status}</span></div><div className="detail-action"><button className="bow-button" onClick={runSelected} disabled={running}>{running ? <LoaderCircle className="spin" size={16} /> : <Sparkles size={16} />}{running ? 'Team is thinking…' : 'Run agent team'}<span className="button-bow">⌁</span></button><small>Only the selected ticket is sent to the boss.</small></div></> : <div className="empty-state"><div className="sleeping">⌒ᴥ⌒</div><p>Select a ticket to see its handoff.</p></div>}</div></div></section>}

      {view === 'team' && <section className="content-section"><div className="section-heading"><div><p className="eyebrow">the atelier roster</p><h2>Agent team</h2></div></div><div className="agent-roster">{Object.entries(AGENTS).map(([key, agent]) => <div className="agent-chip" key={key} style={{ '--agent-accent': agent.accent, '--agent-tint': agent.tint } as CSSProperties}><span>{agent.icon}</span><div><strong>{agent.label}</strong><small>{key === 'boss' ? 'triage & final decisions' : key === 'customer_service' ? 'drafts, never sends' : `${key} desk specialist`}</small></div></div>)}</div></section>}

      {(view === 'activity' || view === 'tickets' || view === 'team') && <section className="content-section"><div className="section-heading"><div><p className="eyebrow">the ribbon trail</p><h2>Agent activity</h2></div><span className="section-note">{recentEvents.length} recent events</span></div><div className="activity-feed">{recentEvents.length ? recentEvents.map((item, index) => { const agent = AGENTS[item.agent_name || ''] || { label: item.agent_name || 'System', icon: '✦', accent: '#9a7890', tint: '#f5eaf0' }; return <article className="activity-row" key={`${item.time}-${index}`}><span className="activity-avatar" style={{ background: agent.tint, color: agent.accent }}>{agent.icon}</span><div className="activity-main"><div className="activity-title"><strong>{agent.label}</strong><span>{item.action?.replace('_', ' ')}</span><time>{item.time ? new Date(item.time).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''}</time></div>{item.result?.summary && <p>{item.result.summary}</p>}{item.result?.actions?.length ? <p className="activity-detail">{item.result.actions.join(' · ')}</p> : null}{item.tool_calls?.length ? <div className="tool-tags">{item.tool_calls.map((tool, i) => <span key={i}><Package size={12} />{tool.tool}</span>)}</div> : null}{item.stop_reason && <small className="stop-reason">{item.stop_reason}</small>}</div></article> }) : <div className="empty-state"><div className="sleeping">⌒ᴥ⌒</div><p>Run a ticket to invite the agents into the activity trail.</p></div>}</div></section>}

      {view === 'approvals' && <section className="content-section"><div className="section-heading"><div><p className="eyebrow">human in the loop</p><h2>Approvals</h2><p className="subhead">Agents can prepare a request. Money moves only after you approve it here.</p></div></div><form className="approval-card" onSubmit={approve}><div className="approval-ribbon"><Sparkles size={16} /> approval atelier</div><div className="form-grid"><label>Request type<select value={approval.kind} onChange={e => setApproval({ ...approval, kind: e.target.value })}><option value="invoice">Invoice payment</option><option value="rent">Rent payment</option><option value="purchase_order">Purchase order</option></select></label><label>Reference ID<input value={approval.ref_id} onChange={e => setApproval({ ...approval, ref_id: e.target.value })} placeholder="e.g. 501" inputMode="numeric" /></label><label>Amount<input required value={approval.amount} onChange={e => setApproval({ ...approval, amount: e.target.value })} placeholder="0.00" type="number" min="0.01" step="0.01" /></label><label>Account<input value={approval.account} onChange={e => setApproval({ ...approval, account: e.target.value })} /></label><label>Human approver<input required value={approval.approved_by} onChange={e => setApproval({ ...approval, approved_by: e.target.value })} placeholder="Your name" /></label><label>Description<input value={approval.description} onChange={e => setApproval({ ...approval, description: e.target.value })} placeholder="What was approved?" /></label></div><button className="bow-button" type="submit"><BadgeCheck size={16} /> Approve and record payment <span className="button-bow">⌁</span></button><p className="form-note">The MCP transaction rejects duplicates, missing accounts, unpaid-shipment violations, and negative balances.</p></form></section>}

      {view === 'cash' && <section className="content-section"><div className="section-heading"><div><p className="eyebrow">the pearl ledger</p><h2>Cash</h2></div><button className="text-button" onClick={refresh}><RefreshCw size={14} /> refresh balance</button></div><div className="cash-display"><div className="cash-orbit"><Banknote size={30} /></div><small>checking · MCP verified</small><strong>{cash ? `$${cash.balance.toLocaleString()}` : '—'}</strong><p>as of {cash?.date || 'the latest desk date'}</p><div className="cash-rule"><span />Human approval before every payment · no negative balances<span /></div></div></section>}
    </main>
  </div>
}

export default App
