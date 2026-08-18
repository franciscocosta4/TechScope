namespace TechScope.Models
{
    public class DashboardViewModel
    {
        // passamos os dados que são necessários para a sidebar:
        public required string FullName { get; set; }
        public required string Email { get; set; }
        public required string Initial { get; set; }
    }
}