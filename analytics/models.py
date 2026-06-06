from django.db import models
from employee.models import Employee

class PerformanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_records')
    year = models.IntegerField()
    month = models.IntegerField()
    attendance_percentage = models.FloatField(default=0.0)
    task_completion_percentage = models.FloatField()
    project_rating = models.FloatField()
    performance_score = models.FloatField(default=0.0)
    ai_grade = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'year', 'month')
        ordering = ['-year', '-month']

    def save(self, *args, **kwargs):
        # Dynamically import to avoid circular imports
        from attendance.views import calculate_attendance_stats
        from .ml import predict_performance_grade
        
        # Calculate attendance stats for the month/year
        stats = calculate_attendance_stats(self.employee, self.year, self.month)
        self.attendance_percentage = stats['attendance_percentage']
        
        # Calculate weighted performance score
        # Formula: 0.4 * Attendance + 0.3 * TaskCompletion + 0.3 * ProjectRating
        self.performance_score = (
            (0.4 * self.attendance_percentage) + 
            (0.3 * self.task_completion_percentage) + 
            (0.3 * self.project_rating)
        )
        
        # Run AI inference to predict and cache grade
        self.ai_grade = predict_performance_grade(
            self.attendance_percentage, 
            self.task_completion_percentage, 
            self.project_rating
        )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.year}/{self.month:02d} - Score: {self.performance_score:.2f} ({self.ai_grade})"
