using System.ComponentModel.DataAnnotations;

namespace TechScope.ViewModels;

public class TechnologyDetailViewModel
{
    public string Keyword { get; set; } = string.Empty;
    public int TotalJobs { get; set; }
    public List<MonthlyTrend> MonthlyTrend { get; set; } = new();
    public List<TechnologyInfo> RelatedTechnologies { get; set; } = new();
    public List<CompanyInfo> TopCompanies { get; set; } = new();
    public List<RecentJobInfo> RecentJobs { get; set; } = new();
}

public class MonthlyTrend
{
    public string Month { get; set; } = string.Empty; // "2024-01"
    public int JobCount { get; set; }
}

public class TechnologyInfo
{
    public string Keyword { get; set; } = string.Empty;
    public int JobCount { get; set; }
}

public class CompanyInfo
{
    public string Name { get; set; } = string.Empty;
    public string? Location { get; set; }
    public int JobCount { get; set; }
}

public class RecentJobInfo
{
    public Guid Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string? CompanyName { get; set; }
    public string? Source { get; set; }
    public string? ExternalId { get; set; }
    public DateTime? DatePosted { get; set; }
}
