namespace TechScope.ViewModels;

public class JobsViewModel
{
    public int TotalJobs { get; set; }
    public int ResultsCounter { get; set; }
    public List<JobsSearchResult> SearchResults { get; set; } = new();
    public List<RecentJobsItem> RecentJobs { get; set; } = new();
    public string? SearchString { get; set; }
    public int PageNumber { get; set; }
    public int PageSize { get; set; }
    
    public int TotalPages => (int)Math.Ceiling((double)TotalJobs / PageSize);


}

public class RecentJobsItem
{
    public string Title { get; set; } = string.Empty;
    public string ExternalId { get; set; } = string.Empty;

}
public class JobsSearchResult
{
    public string Title { get; set; } = string.Empty;
    public string ExternalId { get; set; } = string.Empty;
    public DateOnly? DatePosted { get; set; } 
    public string CompanyName { get; set; } = string.Empty;
    public List<string> Keywords { get; set; } = new();

}
