namespace TechScope.Models
{
public class JobTechnology
{
    public Guid JobId { get; set; }

    public long TechnologyId { get; set; }

    public decimal? ConfidenceScore { get; set; }

    public Job Job { get; set; } = null!;

    public Technology Technology { get; set; } = null!;
}}