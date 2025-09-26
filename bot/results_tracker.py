"""
Results tracker module for monitoring and reporting accepted jobs.
This module provides functionality to track accepted jobs and report results
at regular intervals (e.g., every 5 seconds).
"""

import time
from datetime import datetime
from typing import Any, Dict, List


class ResultsTracker:
    """Tracks and reports accepted and rejected jobs at regular intervals."""
    
    def __init__(self, report_interval: float = 5.0, rejected_report_interval: float = 43200.0):
        """
        Initialize the results tracker.
        
        Args:
            report_interval: Interval in seconds for reporting accepted jobs results
            rejected_report_interval: Interval in seconds for reporting rejected jobs
        """
        self.report_interval = report_interval
        self.rejected_report_interval = rejected_report_interval
        self.last_report_time = time.time()
        self.last_rejected_report_time = time.time()
        self.accepted_jobs: List[Dict[str, Any]] = []
        self.rejected_jobs: List[Dict[str, Any]] = []
        self.total_accepted = 0
        self.total_rejected = 0
        self.session_start_time = time.time()
        self.check_cycles = 0  # Track number of 0.5s check cycles
        self.login_status = "Not attempted"  # Track login status
        self.login_time = None
        self.last_activity_time = None
        
    def add_accepted_job(self, job: Dict[str, Any]) -> None:
        """
        Add an accepted job to the tracker.
        
        Args:
            job: Dictionary containing job information
        """
        job_with_timestamp = {
            **job,
            'accepted_at': datetime.now().isoformat(),
            'accepted_timestamp': time.time()
        }
        self.accepted_jobs.append(job_with_timestamp)
        self.total_accepted += 1
        
    def add_rejected_job(self, job: Dict[str, Any], reason: str = "Unknown") -> None:
        """
        Add a rejected job to the tracker.
        
        Args:
            job: Dictionary containing job information
            reason: Reason for rejection
        """
        job_with_timestamp = {
            **job,
            'rejected_at': datetime.now().isoformat(),
            'rejected_timestamp': time.time(),
            'rejection_reason': reason
        }
        self.rejected_jobs.append(job_with_timestamp)
        self.total_rejected += 1
        
    def increment_check_cycle(self) -> None:
        """Increment the check cycle counter (called every 0.5s)."""
        self.check_cycles += 1
        self.last_activity_time = time.time()
        
    def set_login_status(self, status: str, success: bool = True) -> None:
        """
        Set the login status.
        
        Args:
            status: Status message
            success: Whether login was successful
        """
        self.login_status = f"{'✅' if success else '❌'} {status}"
        if success:
            self.login_time = time.time()
        self.last_activity_time = time.time()
        
    def update_activity(self) -> None:
        """Update the last activity time."""
        self.last_activity_time = time.time()
        
    def should_report(self) -> bool:
        """
        Check if it's time to report accepted jobs results.
        
        Returns:
            True if it's time to report, False otherwise
        """
        current_time = time.time()
        return (current_time - self.last_report_time) >= self.report_interval
        
    def should_report_rejected(self) -> bool:
        """
        Check if it's time to report rejected jobs.
        
        Returns:
            True if it's time to report rejected jobs, False otherwise
        """
        current_time = time.time()
        return (current_time - self.last_rejected_report_time) >= self.rejected_report_interval
        
    def get_results_summary(self) -> Dict[str, Any]:
        """
        Get a summary of accepted jobs since last report.
        
        Returns:
            Dictionary containing results summary
        """
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Get jobs accepted since last report
        jobs_since_last_report = [
            job for job in self.accepted_jobs 
            if job['accepted_timestamp'] > self.last_report_time
        ]
        
        # Calculate time since login
        time_since_login = None
        if self.login_time:
            time_since_login = round(current_time - self.login_time, 1)
            
        # Calculate time since last activity
        time_since_activity = None
        if self.last_activity_time:
            time_since_activity = round(current_time - self.last_activity_time, 1)
            
        return {
            'session_duration_minutes': round(session_duration / 60, 2),
            'session_duration_seconds': round(session_duration, 1),
            'check_cycles': self.check_cycles,
            'login_status': self.login_status,
            'time_since_login': time_since_login,
            'time_since_activity': time_since_activity,
            'total_accepted': self.total_accepted,
            'total_rejected': self.total_rejected,
            'accepted_since_last_report': len(jobs_since_last_report),
            'jobs_since_last_report': jobs_since_last_report,
            'report_time': datetime.now().isoformat()
        }
        
    def get_rejected_summary(self) -> Dict[str, Any]:
        """
        Get a summary of rejected jobs since last rejected report.
        
        Returns:
            Dictionary containing rejected jobs summary
        """
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Get jobs rejected since last rejected report
        jobs_since_last_rejected_report = [
            job for job in self.rejected_jobs 
            if job['rejected_timestamp'] > self.last_rejected_report_time
        ]
        
        return {
            'session_duration_seconds': round(session_duration, 1),
            'check_cycles': self.check_cycles,
            'login_status': self.login_status,
            'total_rejected': self.total_rejected,
            'rejected_since_last_report': len(jobs_since_last_rejected_report),
            'jobs_since_last_rejected_report': jobs_since_last_rejected_report,
            'report_time': datetime.now().isoformat()
        }
        
    def report_rejected_jobs(self) -> None:
        """Report rejected jobs and update last rejected report time."""
        if not self.should_report_rejected():
            return
            
        summary = self.get_rejected_summary()
        self.last_rejected_report_time = time.time()
        
        # Print rejected jobs report
        print(f"\n{'='*70}")
        print(f"❌ REJECTED JOBS REPORT - {summary['report_time']}")
        print(f"{'='*70}")
        print(f"🔐 Login Status: {summary['login_status']}")
        print(f"⏱️  Session: {summary['session_duration_seconds']}s | Cycles: {summary['check_cycles']}")
        print(f"🚫 Total Rejected: {summary['total_rejected']} jobs")
        print(f"🆕 Since Last Report: {summary['rejected_since_last_report']} jobs")
        print(f"⏰ Report Interval: Every 12 hours")
        
        if summary['jobs_since_last_rejected_report']:
            print(f"\n📋 Recently Rejected Jobs:")
            for i, job in enumerate(summary['jobs_since_last_rejected_report'], 1):
                print(f"  {i}. Job {job.get('ref', 'N/A')}: {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')}")
                print(f"     Reason: {job.get('rejection_reason', 'Unknown')} | Rejected at: {job.get('rejected_at', 'N/A')}")
        else:
            print(f"\n📋 No new jobs rejected since last report")
            
        print(f"{'='*50}")
        
    def get_unified_summary(self) -> Dict[str, Any]:
        """
        Get a unified summary of both accepted and rejected jobs since last report.
        
        Returns:
            Dictionary containing unified job summary
        """
        current_time = time.time()
        session_duration = current_time - self.session_start_time
        
        # Get jobs accepted since last report
        jobs_accepted_since_last = [
            job for job in self.accepted_jobs 
            if job['accepted_timestamp'] > self.last_report_time
        ]
        
        # Get jobs rejected since last report
        jobs_rejected_since_last = [
            job for job in self.rejected_jobs 
            if job['rejected_timestamp'] > self.last_report_time
        ]
        
        # Calculate time since login
        time_since_login = None
        if self.login_time:
            time_since_login = round(current_time - self.login_time, 1)
            
        # Calculate time since last activity
        time_since_activity = None
        if self.last_activity_time:
            time_since_activity = round(current_time - self.last_activity_time, 1)
            
        return {
            'session_duration_minutes': round(session_duration / 60, 2),
            'session_duration_seconds': round(session_duration, 1),
            'check_cycles': self.check_cycles,
            'login_status': self.login_status,
            'time_since_login': time_since_login,
            'time_since_activity': time_since_activity,
            'total_accepted': self.total_accepted,
            'total_rejected': self.total_rejected,
            'accepted_since_last_report': len(jobs_accepted_since_last),
            'rejected_since_last_report': len(jobs_rejected_since_last),
            'jobs_accepted_since_last': jobs_accepted_since_last,
            'jobs_rejected_since_last': jobs_rejected_since_last,
            'report_time': datetime.now().isoformat()
        }
        
    def report_results(self) -> None:
        """Report current results and update last report time."""
        if not self.should_report():
            return
            
        summary = self.get_unified_summary()
        self.last_report_time = time.time()
        
        # Print unified results
        print(f"\n{'='*80}")
        print(f"📊 AtoZ BOT RESULTS REPORT - {summary['report_time']}")
        print(f"{'='*80}")
        print(f"🔐 Login Status: {summary['login_status']}")
        if summary['time_since_login']:
            print(f"⏰ Time Since Login: {summary['time_since_login']}s")
        if summary['time_since_activity']:
            print(f"🔄 Last Activity: {summary['time_since_activity']}s ago")
        print(f"⏱️  Session Duration: {summary['session_duration_minutes']} minutes ({summary['session_duration_seconds']}s)")
        print(f"🔄 Check Cycles: {summary['check_cycles']} (every 0.5s)")
        print(f"✅ Jobs Accepted: {summary['total_accepted']} jobs")
        print(f"🚫 Jobs Rejected: {summary['total_rejected']} jobs")
        print(f"📈 Total Processed: {summary['total_accepted'] + summary['total_rejected']} jobs")
        print(f"🆕 Since Last Report: {summary['accepted_since_last_report']} accepted, {summary['rejected_since_last_report']} rejected")
        
        # Show recent activity
        if summary['jobs_accepted_since_last'] or summary['jobs_rejected_since_last']:
            print(f"\n📋 Recent Job Activity:")
            
            # Show accepted jobs first (highlighted)
            if summary['jobs_accepted_since_last']:
                print(f"\n  🎉 ACCEPTED JOBS ({len(summary['jobs_accepted_since_last'])}):")
                for i, job in enumerate(summary['jobs_accepted_since_last'], 1):
                    print(f"    ✅ {i}. Job {job.get('ref', 'N/A')}: {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')}")
                    print(f"       📞 Telephone Translation | Accepted at: {job.get('accepted_at', 'N/A')}")
            
            # Show rejected jobs
            if summary['jobs_rejected_since_last']:
                print(f"\n  ❌ REJECTED JOBS ({len(summary['jobs_rejected_since_last'])}):")
                for i, job in enumerate(summary['jobs_rejected_since_last'], 1):
                    print(f"    🚫 {i}. Job {job.get('ref', 'N/A')}: {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')}")
                    print(f"       Reason: {job.get('rejection_reason', 'Unknown')} | Rejected at: {job.get('rejected_at', 'N/A')}")
        else:
            print(f"\n📋 No new job activity since last report")
            
        print(f"{'='*80}\n")
        
    def print_accepted_job_report(self) -> None:
        """Print a dedicated report of all accepted jobs."""
        if not self.accepted_jobs:
            print(f"\n{'='*60}")
            print(f"📋 ACCEPTED JOB REPORT")
            print(f"{'='*60}")
            print(f"❌ No jobs have been accepted yet.")
            print(f"{'='*60}\n")
            return
            
        print(f"\n{'='*80}")
        print(f"📋 ACCEPTED JOB REPORT")
        print(f"{'='*80}")
        print(f"🔐 Login Status: {self.login_status}")
        print(f"⏱️  Session Duration: {(self.last_activity_time - self.session_start_time) / 60:.1f} minutes" if self.last_activity_time else "Session in progress")
        print(f"🔄 Total Check Cycles: {self.check_cycles}")
        print(f"✅ Total Jobs Accepted: {self.total_accepted}")
        print(f"📞 All accepted jobs are Telephone Translations")
        print(f"{'='*80}")
        
        # Group jobs by language for better organization
        jobs_by_language = {}
        for job in self.accepted_jobs:
            lang = job.get('language', 'Unknown')
            if lang not in jobs_by_language:
                jobs_by_language[lang] = []
            jobs_by_language[lang].append(job)
        
        # Sort languages by number of jobs
        sorted_languages = sorted(jobs_by_language.items(), key=lambda x: len(x[1]), reverse=True)
        
        for lang, jobs in sorted_languages:
            print(f"\n🌍 {lang} ({len(jobs)} jobs):")
            for i, job in enumerate(jobs, 1):
                print(f"  ✅ {i}. Job {job.get('ref', 'N/A')}")
                print(f"     📅 Date: {job.get('appt_date', 'N/A')}")
                print(f"     ⏰ Time: {job.get('appt_time', 'N/A')}")
                print(f"     ⏱️  Duration: {job.get('duration', 'N/A')}")
                print(f"     📞 Type: Telephone Translation")
                print(f"     ✅ Accepted: {job.get('accepted_at', 'N/A')}")
                print()
        
        # Summary statistics
        print(f"{'='*80}")
        print(f"📊 ACCEPTED JOBS SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Total Accepted: {self.total_accepted} jobs")
        print(f"🌍 Languages: {len(jobs_by_language)} different languages")
        print(f"📅 Date Range: {min(job.get('appt_date', '') for job in self.accepted_jobs) if self.accepted_jobs else 'N/A'} to {max(job.get('appt_date', '') for job in self.accepted_jobs) if self.accepted_jobs else 'N/A'}")
        
        # Time distribution
        time_periods = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        for job in self.accepted_jobs:
            try:
                hour = int(job.get('appt_time', '00:00').split(':')[0])
                if 6 <= hour < 12:
                    time_periods['morning'] += 1
                elif 12 <= hour < 17:
                    time_periods['afternoon'] += 1
                elif 17 <= hour < 22:
                    time_periods['evening'] += 1
                else:
                    time_periods['night'] += 1
            except (ValueError, IndexError):
                pass
                
        print(f"🕐 Time Distribution:")
        for period, count in time_periods.items():
            if count > 0:
                print(f"   {period.capitalize()}: {count} jobs")
        
        print(f"{'='*80}\n")
        
    def get_detailed_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics about accepted and rejected jobs.
        
        Returns:
            Dictionary containing detailed statistics
        """
        if not self.accepted_jobs and not self.rejected_jobs:
            return {
                'total_accepted': 0,
                'total_rejected': 0,
                'total_jobs': 0,
                'languages': {},
                'time_periods': {},
                'rejection_reasons': {},
                'average_per_hour': 0,
                'check_cycles': self.check_cycles
            }
            
        # Language distribution (accepted jobs)
        languages = {}
        for job in self.accepted_jobs:
            lang = job.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
            
        # Time period distribution (accepted jobs)
        time_periods = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        for job in self.accepted_jobs:
            try:
                hour = int(job.get('appt_time', '00:00').split(':')[0])
                if 6 <= hour < 12:
                    time_periods['morning'] += 1
                elif 12 <= hour < 17:
                    time_periods['afternoon'] += 1
                elif 17 <= hour < 22:
                    time_periods['evening'] += 1
                else:
                    time_periods['night'] += 1
            except (ValueError, IndexError):
                pass
                
        # Rejection reasons distribution
        rejection_reasons = {}
        for job in self.rejected_jobs:
            reason = job.get('rejection_reason', 'Unknown')
            rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
                
        # Calculate average jobs per hour
        session_duration_hours = (time.time() - self.session_start_time) / 3600
        total_jobs = self.total_accepted + self.total_rejected
        average_per_hour = total_jobs / session_duration_hours if session_duration_hours > 0 else 0
        
        return {
            'total_accepted': self.total_accepted,
            'total_rejected': self.total_rejected,
            'total_jobs': total_jobs,
            'languages': languages,
            'time_periods': time_periods,
            'rejection_reasons': rejection_reasons,
            'average_per_hour': round(average_per_hour, 2),
            'session_duration_hours': round(session_duration_hours, 2),
            'check_cycles': self.check_cycles
        }
        
    def print_detailed_stats(self) -> None:
        """Print detailed statistics about accepted and rejected jobs."""
        stats = self.get_detailed_stats()
        
        print(f"\n{'='*80}")
        print(f"📈 DETAILED STATISTICS")
        print(f"{'='*80}")
        print(f"🔐 Login Status: {self.login_status}")
        print(f"📊 Total Jobs Processed: {stats['total_jobs']}")
        print(f"✅ Jobs Accepted: {stats['total_accepted']}")
        print(f"🚫 Jobs Rejected: {stats['total_rejected']}")
        print(f"⏱️  Session Duration: {stats['session_duration_hours']} hours")
        print(f"🔄 Check Cycles: {stats['check_cycles']} (every 0.5s)")
        print(f"📈 Average per Hour: {stats['average_per_hour']} jobs")
        
        if stats['languages']:
            print(f"\n🌍 Language Distribution (Accepted):")
            for lang, count in sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {lang}: {count} jobs")
                
        if stats['time_periods']:
            print(f"\n🕐 Time Period Distribution (Accepted):")
            for period, count in stats['time_periods'].items():
                print(f"  {period.capitalize()}: {count} jobs")
                
        if stats['rejection_reasons']:
            print(f"\n❌ Rejection Reasons:")
            for reason, count in sorted(stats['rejection_reasons'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count} jobs")
                
        print(f"{'='*70}\n")


# Global tracker instance
_tracker = None

def get_tracker() -> ResultsTracker:
    """Get the global results tracker instance."""
    global _tracker
    if _tracker is None:
        _tracker = ResultsTracker()
    return _tracker

def initialize_tracker(report_interval: float = 5.0, rejected_report_interval: float = 43200.0) -> ResultsTracker:
    """Initialize the global results tracker with custom intervals."""
    global _tracker
    _tracker = ResultsTracker(report_interval, rejected_report_interval)
    return _tracker

def add_accepted_job(job: Dict[str, Any]) -> None:
    """Add an accepted job to the global tracker."""
    get_tracker().add_accepted_job(job)

def add_rejected_job(job: Dict[str, Any], reason: str = "Unknown") -> None:
    """Add a rejected job to the global tracker."""
    get_tracker().add_rejected_job(job, reason)

def increment_check_cycle() -> None:
    """Increment the check cycle counter (called every 0.5s)."""
    get_tracker().increment_check_cycle()

def set_login_status(status: str, success: bool = True) -> None:
    """Set the login status in the global tracker."""
    get_tracker().set_login_status(status, success)

def update_activity() -> None:
    """Update the last activity time in the global tracker."""
    get_tracker().update_activity()

def check_and_report() -> None:
    """Check if it's time to report and report if necessary."""
    get_tracker().report_results()

def check_and_report_rejected() -> None:
    """Check if it's time to report rejected jobs and report if necessary."""
    get_tracker().report_rejected_jobs()

def print_detailed_stats() -> None:
    """Print detailed statistics using the global tracker."""
    get_tracker().print_detailed_stats()

def print_accepted_job_report() -> None:
    """Print accepted job report using the global tracker."""
    get_tracker().print_accepted_job_report()
