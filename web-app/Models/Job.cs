namespace TechScope.Models
{
public class Job
{
    public Guid Id { get; set; }

    public Guid CompanyId { get; set; }

    public string Title { get; set; } = null!;

    public string? Location { get; set; }

    public decimal? SalaryMin { get; set; }

    public decimal? SalaryMax { get; set; }

    public string? Description { get; set; }

    public string Source { get; set; } = null!;

    public string ExternalId { get; set; } = null!;

    public DateTime? DatePosted { get; set; }

    public DateTime CreatedAt { get; set; }

    public Company Company { get; set; } = null!;
    // public ICollection<JobTechnology> JobTechnologies { get; set; } = new List<JobTechnology>();
    
}
}