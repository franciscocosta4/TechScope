namespace TechScope.Models
{
public class Company
{
    public Guid Id { get; set; }

    public string Name { get; set; } = null!;

    public string? Website { get; set; }

    public string? Location { get; set; }

    public DateTime CreatedAt { get; set; }

    public ICollection<Job> Jobs { get; set; } = new List<Job>();
}}