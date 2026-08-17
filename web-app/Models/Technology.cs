using System.ComponentModel.DataAnnotations;

// namespace TechScope.Models;
namespace TechScope.Models
{
public class Technology
{
    public long Id { get; set; }

    [Required]
    public string Name { get; set; } = null!;

    public string? Category { get; set; }

    public DateTime CreatedAt { get; set; }

    public ICollection<JobTechnology> JobTechnologies { get; set; } = new List<JobTechnology>();
}
}