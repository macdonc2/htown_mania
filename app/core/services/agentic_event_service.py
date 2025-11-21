"""
Agentic Event Service - Uses multi-agent system for event discovery and promo generation.
"""
from typing import List

from app.core.domain.models import Event
from app.core.domain.agent_models import PlanningState, AgentPhase
from app.core.ports.agent_port import PlanningAgentPort
from app.core.ports.sms_port import SMSPort
from app.core.ports.event_repository_port import EventRepositoryPort


class AgenticEventService:
    """
    Event service that uses the agentic workflow.
    
    This service orchestrates the multi-agent system:
    1. Planning agent coordinates everything
    2. Search agents run in parallel
    3. Review swarm validates/enriches
    4. Promo agent generates final output
    """
    
    def __init__(
        self,
        planning_agent: PlanningAgentPort,
        sms: SMSPort,
        repository: EventRepositoryPort,
        sms_recipient: str,
        dev_sms_mute: int = 0
    ):
        self.planning_agent = planning_agent
        self.sms = sms
        self.repository = repository
        self.sms_recipient = sms_recipient
        self.dev_sms_mute = dev_sms_mute
        self.dry_run = False  # Can be set externally for full dry run (no DB, no SMS)
        self.no_db = False  # Can be set externally to skip DB but send email
    
    async def run_daily_event_flow(self, enable_research: bool = False) -> str:
        """
        Run the complete agentic workflow.
        
        Args:
            enable_research: If True, enables deep research phase
        
        Returns:
            The generated promo text
        """
        print("\n" + "="*80)
        if enable_research:
            print("🔬 STARTING DEEP RESEARCH EVENT WORKFLOW (Agentic + Research)")
        else:
            print("🤖 STARTING AGENTIC EVENT WORKFLOW")
        print("="*80 + "\n")
        
        # Initialize state
        initial_state = PlanningState(
            phase=AgentPhase.INITIALIZING,
            research_enabled=enable_research  # Enable/disable research
        )
        
        # Run the planning agent workflow
        final_state = await self.planning_agent.run_workflow(initial_state)
        
        # Check if successful
        if final_state.phase == AgentPhase.FAILED:
            error_msg = f"Workflow failed: {final_state.error_message}"
            print(f"\n❌ {error_msg}\n")
            return error_msg
        
        if not final_state.promo_generated:
            error_msg = "No promo was generated"
            print(f"\n❌ {error_msg}\n")
            return error_msg
        
        # Extract the promo
        promo_text = final_state.promo_generated
        
        # Format events for the listing
        events_to_save = [enriched.event for enriched in final_state.events_reviewed]
        event_listing = self._format_event_listing(events_to_save)
        
        # Format the scratchpad for the email
        scratchpad_text = self._format_scratchpad(final_state)
        
        # Build the full message: Promo + Event Listing + Scratchpad
        full_message = promo_text + event_listing + scratchpad_text
        
        # Save events to repository (skip in dry-run or no-db mode)
        if self.dry_run:
            print(f"🧪 [DRY RUN] Skipping DB save of {len(events_to_save)} events")
        elif self.no_db:
            print(f"🗄️  [NO-DB] Skipping DB save of {len(events_to_save)} events (no PostgreSQL needed)")
        elif events_to_save:
            await self.repository.save_events(events_to_save)
            print(f"💾 Saved {len(events_to_save)} events to repository")
        
        # Send SMS/Email (skip only in dry-run mode, NOT in no-db mode)
        if self.dry_run:
            print(f"🧪 [DRY RUN] Skipping SMS to {self.sms_recipient}")
        elif not self.dev_sms_mute:
            # Pass events, promo, and scratchpad for HTML email rendering
            await self.sms.send_sms(
                self.sms_recipient, 
                full_message,
                events=events_to_save,
                promo_text=promo_text,
                scratchpad_text=scratchpad_text
            )
            print(f"📱 Email/SMS sent to {self.sms_recipient}")
        else:
            print(f"[DEV_SMS_MUTE=1] SMS would be sent to {self.sms_recipient}")
        
        # Print summary
        print("\n" + "="*80)
        print("✅ AGENTIC WORKFLOW COMPLETE")
        print("="*80)
        print("📊 Stats:")
        print(f"  - Events found: {len(final_state.events_found)}")
        print(f"  - Events reviewed: {len(final_state.events_reviewed)}")
        print(f"  - Search sources: {', '.join(final_state.search_sources_completed)}")
        print(f"  - Questions raised: {len(final_state.questions_to_investigate)}")
        print(f"  - Observations logged: {len(final_state.scratchpad)}")
        
        verified = sum(1 for e in final_state.events_reviewed if e.verified)
        print(f"  - Verified events: {verified}/{len(final_state.events_reviewed)}")
        
        if final_state.events_reviewed:
            avg_conf = sum(e.confidence_score for e in final_state.events_reviewed) / len(final_state.events_reviewed)
            print(f"  - Avg confidence: {avg_conf:.2f}")
        
        if enable_research and final_state.events_researched:
            print(f"  - Events researched: {len(final_state.events_researched)}")
        
        if self.dry_run:
            print("\n🧪 DRY RUN MODE: No data was saved to database or sent via SMS")
        elif self.no_db:
            print("\n🗄️  NO-DB MODE: Database save skipped, but email was sent!")
        
        print("="*80 + "\n")
        
        # Optionally print the scratchpad for transparency
        self._print_scratchpad(final_state)
        
        return full_message
    
    def _format_event_listing(self, events: List[Event]) -> str:
        """Format events into a plain text listing."""
        if not events:
            return ""
        
        listing_lines = [
            "\n\n" + "=" * 60,
            "COMPLETE EVENT LISTING",
            "=" * 60,
            ""
        ]
        
        for idx, event in enumerate(events, 1):
            listing_lines.append(f"{idx}. {event.title.upper()}")
            
            if event.url:
                listing_lines.append(f"   {event.url}")
            
            details = []
            if event.location:
                details.append(f"Location: {event.location}")
            if event.start_time:
                time_str = event.start_time.strftime("%a, %b %d at %I:%M %p")
                details.append(f"Time: {time_str}")
            if details:
                listing_lines.append(f"   {' | '.join(details)}")
            
            if event.categories:
                cats = ", ".join(event.categories)
                listing_lines.append(f"   Categories: {cats}")
            
            listing_lines.append("")
        
        listing_lines.append("=" * 60)
        
        return "\n".join(listing_lines)
    
    def _format_scratchpad(self, state: PlanningState) -> str:
        """Format the planning agent's scratchpad for inclusion in the message."""
        lines = [
            "\n\n" + "=" * 60,
            "🤖 AGENT REASONING TRACE (How We Did It!)",
            "=" * 60,
            ""
        ]
        
        for i, obs in enumerate(state.scratchpad, 1):
            lines.append(f"[{i}] {obs.agent} @ {obs.timestamp.strftime('%H:%M:%S')}")
            lines.append(f"    💭 Thought: {obs.thought}")
            if obs.action:
                lines.append(f"    🎯 Action: {obs.action}")
            if obs.result:
                lines.append(f"    👁️  Observation: {obs.result}")
            lines.append(f"    📊 Confidence: {obs.confidence:.2f}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _print_scratchpad(self, state: PlanningState):
        """Print the planning agent's scratchpad for transparency."""
        print("\n" + "="*80)
        print("📝 PLANNING AGENT SCRATCHPAD (REACT TRACE)")
        print("="*80 + "\n")
        
        for i, obs in enumerate(state.scratchpad, 1):
            print(f"[{i}] {obs.agent} @ {obs.timestamp.strftime('%H:%M:%S')}")
            print(f"    💭 Thought: {obs.thought}")
            if obs.action:
                print(f"    🎯 Action: {obs.action}")
            if obs.result:
                print(f"    👁️  Observation: {obs.result}")
            print(f"    📊 Confidence: {obs.confidence:.2f}")
            print()
        
        print("="*80 + "\n")

