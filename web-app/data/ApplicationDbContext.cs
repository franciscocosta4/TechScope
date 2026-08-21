using Microsoft.EntityFrameworkCore;
using TechScope.Models;

namespace TechScope.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<Company> Companies => Set<Company>();
        public DbSet<Job> Jobs => Set<Job>();
        public DbSet<JobKeyword> JobKeywords => Set<JobKeyword>();

        protected override void OnModelCreating(ModelBuilder builder)
        {
            builder.Entity<Company>()
                .ToTable("Companies", table => table.ExcludeFromMigrations());
            builder.Entity<Company>()
                .HasKey(company => company.Id);

            builder.Entity<Job>()
                .ToTable("Jobs", table => table.ExcludeFromMigrations());
            builder.Entity<Job>()
                .HasKey(job => job.Id);
            builder.Entity<Job>()
                .HasOne(job => job.Company)
                .WithMany(company => company.Jobs)
                .HasForeignKey(job => job.CompanyId)
                .OnDelete(DeleteBehavior.Cascade);

            builder.Entity<JobKeyword>()
                .ToTable("JobKeywords", table => table.ExcludeFromMigrations());
            builder.Entity<JobKeyword>()
                .HasKey(jk => new { jk.JobId, jk.Keyword, jk.Category });
            builder.Entity<JobKeyword>()
                .HasOne(jk => jk.Job)
                .WithMany()
                .HasForeignKey(jk => jk.JobId)
                .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
