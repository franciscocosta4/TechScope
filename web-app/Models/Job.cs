namespace TechScope.Models
{
public class Job
{
    public Guid Id { get; set; }

    public Guid CompanyId { get; set; }

    public string Title { get; set; } = null!;
    public string Location { get; set; } = null!;

    public string Source { get; set; } = null!;

    public string ExternalId { get; set; } = null!;

    public DateOnly? DatePosted { get; set; }

    public DateTime CreatedAt { get; set; }

    public Company Company { get; set; } = null!;
    
    public ICollection<JobKeyword> Keywords { get; set; } = new List<JobKeyword>(); // adicionamos isto para podermos ter a relação Job → JobKeyword(s)

}
}