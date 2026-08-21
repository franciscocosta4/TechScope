namespace TechScope.Models;

public class JobKeyword
{
    public Guid JobId { get; set; }
    public string Keyword { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public Job? Job { get; set; }
}
